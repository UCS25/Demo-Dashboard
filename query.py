# query.py - Complete Query Module for All Tabs (PANDAS-based)
"""
All queries & transformations used by the BLSH Dashboard.
Uses pandas for robustness with varying CSV column names and date formats.
"""

import pandas as pd
from datetime import datetime, timedelta

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _to_datetime_safe(series, formats=None):
    """Try multiple formats and fall back to pandas auto parse."""
    if formats is None:
        formats = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in formats:
        try:
            converted = pd.to_datetime(series, format=fmt, errors="coerce")
            # If at least one non-na parsed, accept it (but keep attempt to fill others)
            if converted.notna().any():
                return converted
        except Exception:
            pass
    # last resort: let pandas infer
    return pd.to_datetime(series, errors="coerce")

def safe_datetime_convert(df, column_candidates):
    """
    Returns a Series of datetimes for the first matching column in column_candidates
    that exists in df. If none present, returns a Series of NaT.
    """
    for col in column_candidates:
        if col in df.columns:
            return _to_datetime_safe(df[col])
    # not found
    return pd.Series([pd.NaT]*len(df), index=df.index)

# ============================================================================
# PREPROCESSING (use this at top of app after loading CSVs)
# ============================================================================

def preprocess_data(df):
    """Create a unified Timestamp column and Date, Month, Week, Year columns."""
    if df is None or df.empty:
        return pd.DataFrame()  # return empty df
    df = df.copy()

    # 1) Find a timestamp column: prefer 'Timestamp', then 'DateTime', then any obvious 'Bill Date & Time' or 'Bill Date'
    timestamp_cols = ['Timestamp', 'DateTime', 'Bill Date & Time', 'Bill Date', 'Timestamp ']
    df['Timestamp'] = safe_datetime_convert(df, timestamp_cols)

    # If Timestamp is still all NaT, check if there is a 'Date' column (like booking Appointment Date)
    if df['Timestamp'].isna().all():
        # also try common date columns
        df['Timestamp'] = safe_datetime_convert(df, ['Date', 'Appointment Date', 'Bill Date'])

    # Extract helpful columns if Timestamp valid
    if 'Timestamp' in df.columns:
        # ensure timestamp dtype
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        if not df['Timestamp'].isna().all():
            df['Date'] = df['Timestamp'].dt.date
            df['Month'] = df['Timestamp'].dt.month_name()
            # week as integer
            df['Week'] = df['Timestamp'].dt.isocalendar().week
            df['Year'] = df['Timestamp'].dt.year
    return df

# ============================================================================
# TAB 1: HOME DASHBOARD QUERIES (pandas implementations)
# ============================================================================

def today_sales(df):
    """Return DataFrame with total_sales_today"""
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"total_sales_today": [0.0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    mask = df2['Timestamp'].dt.normalize() == today
    total = df2.loc[mask, "Bill Amount"].sum(min_count=1)
    total = float(total) if pd.notna(total) else 0.0
    return pd.DataFrame({"total_sales_today": [total]})

def today_customer_count(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"customers_today": [0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    mask = df2['Timestamp'].dt.normalize() == today
    cnt = int(df2.loc[mask, "Name"].nunique()) if "Name" in df2.columns else 0
    return pd.DataFrame({"customers_today": [cnt]})

def new_and_repeated_clients(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return 0, 0
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    df2['Date_only'] = df2['Timestamp'].dt.date
    today = pd.Timestamp.now().date()
    past = df2[df2['Date_only'] < today]
    today_df = df2[df2['Date_only'] == today]
    if 'Phone Number' not in df2.columns:
        return 0, 0
    past_phones = past['Phone Number'].dropna().astype(str).unique().tolist()
    new_clients = today_df[~today_df['Phone Number'].astype(str).isin(past_phones)]
    repeated = today_df[today_df['Phone Number'].astype(str).isin(past_phones)]
    return len(new_clients), len(repeated)

def weekly_service_sales(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"weekly_sales": [0.0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    now = pd.Timestamp.now()
    cw = now.isocalendar().week
    cy = now.year
    mask = (df2['Timestamp'].dt.isocalendar().week == cw) & (df2['Timestamp'].dt.year == cy)
    total = df2.loc[mask, "Bill Amount"].sum(min_count=1)
    return pd.DataFrame({"weekly_sales":[float(total) if pd.notna(total) else 0.0]})

def weekly_service_count(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"weekly_service_count":[0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    now = pd.Timestamp.now()
    cw = now.isocalendar().week
    cy = now.year
    mask = (df2['Timestamp'].dt.isocalendar().week == cw) & (df2['Timestamp'].dt.year == cy)
    subset = df2.loc[mask].copy()
    if 'Phone Number' not in subset.columns:
        return pd.DataFrame({"weekly_service_count":[len(subset)]})
    subset['unique_visit'] = subset['Phone Number'].astype(str) + subset['Timestamp'].dt.date.astype(str)
    return pd.DataFrame({"weekly_service_count":[int(subset['unique_visit'].nunique())]})

def monthly_service_sales(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"monthly_sales":[0.0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    now = pd.Timestamp.now()
    m = now.month
    y = now.year
    mask = (df2['Timestamp'].dt.month == m) & (df2['Timestamp'].dt.year == y)
    total = df2.loc[mask, "Bill Amount"].sum(min_count=1)
    return pd.DataFrame({"monthly_sales":[float(total) if pd.notna(total) else 0.0]})

def monthly_service_count(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"monthly_service_count":[0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    now = pd.Timestamp.now()
    m = now.month
    y = now.year
    mask = (df2['Timestamp'].dt.month == m) & (df2['Timestamp'].dt.year == y)
    subset = df2.loc[mask].copy()
    if 'Phone Number' not in subset.columns:
        return pd.DataFrame({"monthly_service_count":[len(subset)]})
    subset['unique_visit'] = subset['Phone Number'].astype(str) + subset['Timestamp'].dt.date.astype(str)
    return pd.DataFrame({"monthly_service_count":[int(subset['unique_visit'].nunique())]})

def prev_week_service_sales(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"prev_week_sales":[0.0]})
    now = pd.Timestamp.now()
    prev = now - timedelta(weeks=1)
    prev_w = prev.isocalendar().week
    prev_y = prev.year
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    mask = (df2['Timestamp'].dt.isocalendar().week == prev_w) & (df2['Timestamp'].dt.year == prev_y)
    total = df2.loc[mask, "Bill Amount"].sum(min_count=1)
    return pd.DataFrame({"prev_week_sales":[float(total) if pd.notna(total) else 0.0]})

def prev_week_service_count(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"prev_week_service_count":[0]})
    now = pd.Timestamp.now()
    prev = now - timedelta(weeks=1)
    prev_w = prev.isocalendar().week
    prev_y = prev.year
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    subset = df2[(df2['Timestamp'].dt.isocalendar().week == prev_w) & (df2['Timestamp'].dt.year == prev_y)].copy()
    if subset.empty:
        return pd.DataFrame({"prev_week_service_count":[0]})
    if 'Phone Number' not in subset.columns:
        return pd.DataFrame({"prev_week_service_count":[len(subset)]})
    subset['unique_visit'] = subset['Phone Number'].astype(str) + subset['Timestamp'].dt.date.astype(str)
    return pd.DataFrame({"prev_week_service_count":[int(subset['unique_visit'].nunique())]})

def prev_month_service_sales(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"prev_month_sales":[0.0]})
    now = pd.Timestamp.now()
    first_this_month = now.replace(day=1)
    last_prev_month = first_this_month - timedelta(days=1)
    pm = last_prev_month.month
    py = last_prev_month.year
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    mask = (df2['Timestamp'].dt.month == pm) & (df2['Timestamp'].dt.year == py)
    total = df2.loc[mask, "Bill Amount"].sum(min_count=1)
    return pd.DataFrame({"prev_month_sales":[float(total) if pd.notna(total) else 0.0]})

def prev_month_service_count(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"prev_month_service_count":[0]})
    now = pd.Timestamp.now()
    first_this_month = now.replace(day=1)
    last_prev_month = first_this_month - timedelta(days=1)
    pm = last_prev_month.month
    py = last_prev_month.year
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    subset = df2[(df2['Timestamp'].dt.month == pm) & (df2['Timestamp'].dt.year == py)].copy()
    if subset.empty:
        return pd.DataFrame({"prev_month_service_count":[0]})
    if 'Phone Number' not in subset.columns:
        return pd.DataFrame({"prev_month_service_count":[len(subset)]})
    subset['unique_visit'] = subset['Phone Number'].astype(str) + subset['Timestamp'].dt.date.astype(str)
    return pd.DataFrame({"prev_month_service_count":[int(subset['unique_visit'].nunique())]})

def total_service_count(df):
    if df is None or df.empty:
        return pd.DataFrame({"total_services":[0]})
    if "Bill Amount" in df.columns:
        total = df["Bill Amount"].count()
    else:
        total = len(df)
    return pd.DataFrame({"total_services":[int(total)]})

def total_product_sales(df):
    if df is None or df.empty or "Bill Amount" not in df.columns:
        return pd.DataFrame({"total_product_revenue":[0.0]})
    total = df["Bill Amount"].sum(min_count=1)
    return pd.DataFrame({"total_product_revenue":[float(total) if pd.notna(total) else 0.0]})

def total_products_sold(df):
    if df is None or df.empty:
        return pd.DataFrame({"total_products_sold":[0]})
    return pd.DataFrame({"total_products_sold":[int(len(df))]})

def products_sold_today(df):
    if df is None or df.empty:
        return pd.DataFrame({"products_sold_today":[0]})
    df2 = df.copy()
    # prefer Timestamp then DateTime
    df2['Timestamp'] = safe_datetime_convert(df2, ['Timestamp', 'DateTime'])
    df2 = df2.dropna(subset=['Timestamp'])
    if df2.empty:
        return pd.DataFrame({"products_sold_today":[0]})
    today = pd.Timestamp.now().normalize()
    cnt = df2[df2['Timestamp'].dt.normalize() == today].shape[0]
    return pd.DataFrame({"products_sold_today":[int(cnt)]})

def products_sold_last_week(df):
    if df is None or df.empty:
        return pd.DataFrame({"products_sold_last_week":[0]})
    df2 = df.copy()
    df2['Timestamp'] = safe_datetime_convert(df2, ['Timestamp', 'DateTime'])
    df2 = df2.dropna(subset=['Timestamp'])
    if df2.empty:
        return pd.DataFrame({"products_sold_last_week":[0]})
    week_ago = pd.Timestamp.now() - timedelta(days=7)
    cnt = df2[df2['Timestamp'] >= week_ago].shape[0]
    return pd.DataFrame({"products_sold_last_week":[int(cnt)]})

def products_sold_last_month(df):
    if df is None or df.empty:
        return pd.DataFrame({"products_sold_last_month":[0]})
    df2 = df.copy()
    df2['Timestamp'] = safe_datetime_convert(df2, ['Timestamp', 'DateTime'])
    df2 = df2.dropna(subset=['Timestamp'])
    if df2.empty:
        return pd.DataFrame({"products_sold_last_month":[0]})
    month_ago = pd.Timestamp.now() - timedelta(days=30)
    cnt = df2[df2['Timestamp'] >= month_ago].shape[0]
    return pd.DataFrame({"products_sold_last_month":[int(cnt)]})

# ============================================================================
# TAB 2: SERVICE DATA QUERIES (pandas)
# ============================================================================

def cumulative_sales(df):
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return pd.DataFrame({"month_sales":[0.0], "year_sales":[0.0]})
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    now = pd.Timestamp.now()
    month_sales = df2[(df2['Timestamp'].dt.month == now.month) & (df2['Timestamp'].dt.year == now.year)]["Bill Amount"].sum(min_count=1)
    year_sales = df2[df2['Timestamp'].dt.year == now.year]["Bill Amount"].sum(min_count=1)
    return pd.DataFrame({"month_sales":[float(month_sales) if pd.notna(month_sales) else 0.0],
                         "year_sales":[float(year_sales) if pd.notna(year_sales) else 0.0]})

def incentive_table(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["employee","total_sales","incentive"])
    if "Service done by" not in df.columns:
        # return empty frame but keep column names expected by app
        return pd.DataFrame(columns=["employee","total_sales","incentive"])
    grp = df.groupby("Service done by", dropna=True)["Bill Amount"].agg(total_sales="sum").reset_index().rename(columns={"Service done by":"employee"})
    if grp.empty:
        grp["incentive"] = []
    else:
        grp["incentive"] = (grp["total_sales"] * 0.01).round(2)
    grp = grp.sort_values("total_sales", ascending=False).reset_index(drop=True)
    return grp[["employee","total_sales","incentive"]]

def performance_table(df, selected_month=None):
    if df is None or df.empty:
        return pd.DataFrame(columns=["Year","Month","Week","customer_visits"])
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    three_months_ago = pd.Timestamp.now() - timedelta(days=90)
    df2 = df2[df2['Timestamp'] >= three_months_ago]
    if selected_month and selected_month != "All months":
        df2 = df2[df2['Timestamp'].dt.month_name() == selected_month]
    df2['Year'] = df2['Timestamp'].dt.year
    df2['Month'] = df2['Timestamp'].dt.month_name()
    df2['Week'] = df2['Timestamp'].dt.isocalendar().week
    res = df2.groupby(['Year','Month','Week']).agg(customer_visits=('Name','nunique')).reset_index().sort_values(['Year','Week'], ascending=[False, False])
    return res

def peak_hours(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["hour","visit_count"])
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    df2['hour'] = df2['Timestamp'].dt.hour
    res = df2.groupby('hour').size().reset_index(name='visit_count').sort_values('visit_count', ascending=False)
    return res

def weekday_visit_counts(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["weekday","visit_count"])
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    df2['weekday'] = df2['Timestamp'].dt.day_name()
    df2['weekday_num'] = df2['Timestamp'].dt.dayofweek + 1
    res = df2.groupby(['weekday','weekday_num']).size().reset_index(name='visit_count').sort_values('weekday_num')
    return res[['weekday','visit_count']]

def service_count(df, selected_month=None):
    if df is None or df.empty:
        return pd.DataFrame(columns=["Service","count"])
    df2 = df.copy()
    if selected_month and selected_month != "All months":
        df2 = df2[df2['Timestamp'].dt.month_name() == selected_month]
    # melt services; only include known service columns that exist
    services_columns = [c for c in ["Waxing","Facial","De-tan","Pedicure","Manicure","Bleaching","Wash","Massage","Threading","Hair Cut"] if c in df2.columns]
    if not services_columns:
        return pd.DataFrame(columns=["Service","count"])
    melted = df2.melt(id_vars=["Name","Timestamp"], value_vars=services_columns, var_name="Service", value_name="Used")
    melted = melted[melted["Used"].astype(str).str.strip().str.lower().isin(['true','1','yes','y']) | (melted["Used"].notna() & melted["Used"].astype(str).str.strip() != '')]
    res = melted.groupby('Service').size().reset_index(name='count').sort_values('count', ascending=False)
    return res

def top_clients_spend_visits(df):
    if df is None or df.empty or 'Phone Number' not in df.columns:
        return pd.DataFrame(columns=["phone_number","name","visits","total_spent"])
    df2 = df.copy()
    grp = df2.groupby('Phone Number').agg(
        visits = ('Phone Number','count'),
        total_spent = ('Bill Amount','sum')
    ).reset_index().rename(columns={'Phone Number':'phone_number'})
    # get a name per phone using first non-null
    name_map = df2.groupby('Phone Number')['Name'].first().reset_index().rename(columns={'Name':'name','Phone Number':'phone_number'})
    res = grp.merge(name_map, on='phone_number', how='left')[['phone_number','name','visits','total_spent']].sort_values('total_spent', ascending=False).head(20)
    return res

def least_clients_spend_visits(df):
    if df is None or df.empty or 'Phone Number' not in df.columns:
        return pd.DataFrame(columns=["phone_number","name","visits","total_spent"])
    df2 = df.copy()
    grp = df2.groupby('Phone Number').agg(visits=('Phone Number','count'), total_spent=('Bill Amount','sum')).reset_index().rename(columns={'Phone Number':'phone_number'})
    name_map = df2.groupby('Phone Number')['Name'].first().reset_index().rename(columns={'Name':'name','Phone Number':'phone_number'})
    res = grp.merge(name_map, on='phone_number', how='left')[['phone_number','name','visits','total_spent']].sort_values('total_spent', ascending=True).head(20)
    return res

def spend_vs_visits(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["Name","visits","total_spent","avg_spend_per_visit"])
    df2 = df.copy()
    res = df2.groupby('Name').agg(visits=('Name','count'), total_spent=('Bill Amount','sum')).reset_index()
    res['avg_spend_per_visit'] = (res['total_spent'] / res['visits']).round(2)
    return res.sort_values('total_spent', ascending=False)

def days_since_last_visit(df):
    if df is None or df.empty or 'Phone Number' not in df.columns:
        return pd.DataFrame(columns=['Phone Number','Customer_Name','Last_Visit_Date','Days Since Last Visit'])
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], errors='coerce')
    df2['visit_date'] = df2['Timestamp'].dt.date
    df2['phone_clean'] = df2['Phone Number'].astype(str).str.replace(' ', '').str.replace('+91','').str.replace('-','').str.strip()
    latest = df2.sort_values('Timestamp').groupby(['phone_clean','visit_date']).last().reset_index()
    latest2 = latest.groupby('phone_clean').agg(PhoneNumber=('Phone Number','first'), Name=('Name','first'), Last_Visit_Date=('visit_date','max')).reset_index()
    today = pd.Timestamp.now().date()
    latest2['Days Since Last Visit'] = latest2['Last_Visit_Date'].apply(lambda d: (today - d).days if pd.notna(d) else None)
    latest2 = latest2.sort_values('Days Since Last Visit', ascending=False)
    latest2 = latest2.rename(columns={'PhoneNumber':'Phone Number', 'Name':'Customer_Name'})
    return latest2[['Phone Number','Customer_Name','Last_Visit_Date','Days Since Last Visit']]

def employee_service_ranking(df):
    if df is None or df.empty or "Service done by" not in df.columns:
        return pd.DataFrame(columns=["employee","service_count"])
    df2 = df.copy()
    res = df2.groupby("Service done by").size().reset_index(name='service_count').rename(columns={"Service done by":"employee"}).sort_values('service_count', ascending=False)
    return res

def employee_revenue_ranking(df):
    if df is None or df.empty or "Service done by" not in df.columns:
        return pd.DataFrame(columns=["employee","total_revenue"])
    df2 = df.copy()
    res = df2.groupby("Service done by")['Bill Amount'].sum().reset_index().rename(columns={"Service done by":"employee","Bill Amount":"total_revenue"}).sort_values('total_revenue', ascending=False)
    return res

def unique_service_counts(df, selected_month=None):
    return service_count(df, selected_month)

# ============================================================================
# TAB 3: PRODUCT DATA QUERIES (pandas)
# ============================================================================

def get_employee_sales(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["employee","total_products_sold"])
    if 'Sold by' not in df.columns:
        return pd.DataFrame(columns=["employee","total_products_sold"])
    df2 = df.copy()
    res = df2.groupby('Sold by').size().reset_index(name='total_products_sold').rename(columns={'Sold by':'employee'}).sort_values('total_products_sold', ascending=False)
    return res

def get_employee_revenue(df):
    if df is None or df.empty or 'Sold by' not in df.columns:
        return pd.DataFrame(columns=["employee","total_revenue"])
    df2 = df.copy()
    res = df2.groupby('Sold by')['Bill Amount'].sum().reset_index().rename(columns={'Sold by':'employee','Bill Amount':'total_revenue'}).sort_values('total_revenue', ascending=False)
    return res

def get_revenue_summary(df):
    if df is None or df.empty or 'Bill Amount' not in df.columns:
        return {"total_revenue":0.0, "total_sales":0}
    total = float(df['Bill Amount'].sum(min_count=1)) if pd.notna(df['Bill Amount'].sum(min_count=1)) else 0.0
    total_sales = int(len(df))
    return {"total_revenue": total, "total_sales": total_sales}

def get_top_products(df):
    if df is None or df.empty or 'Product Name' not in df.columns:
        return pd.DataFrame(columns=['product','sold_count'])
    df2 = df.copy()
    res = df2.groupby('Product Name').size().reset_index(name='sold_count').rename(columns={'Product Name':'product'}).sort_values('sold_count', ascending=False)
    return res

def get_sales_by_day(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=['day_of_week','total_sold','total_orders'])
    df2 = df.copy()
    df2['Timestamp'] = safe_datetime_convert(df2, ['Timestamp','DateTime'])
    df2 = df2.dropna(subset=['Timestamp'])
    if df2.empty:
        return pd.DataFrame(columns=['day_of_week','total_sold','total_orders'])
    df2['day_of_week'] = df2['Timestamp'].dt.day_name()
    df2['day_num'] = df2['Timestamp'].dt.dayofweek
    res = df2.groupby(['day_of_week','day_num']).agg(total_sold=('Bill Amount','sum'), total_orders=('Bill Amount','count')).reset_index().sort_values('day_num')
    return res[['day_of_week','total_sold','total_orders']]

def get_incentive_by_employee(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=['employee','incentive_amount'])
    df2 = df.copy()
    df2['Timestamp'] = safe_datetime_convert(df2, ['Timestamp','DateTime'])
    df2 = df2.dropna(subset=['Timestamp'])
    if df2.empty:
        return pd.DataFrame(columns=['employee','incentive_amount'])
    current_year = datetime.now().year
    df_year = df2[df2['Timestamp'].dt.year == current_year]
    if df_year.empty or 'Sold by' not in df_year.columns:
        return pd.DataFrame(columns=['employee','incentive_amount'])
    res = df_year.groupby('Sold by')['Bill Amount'].sum().reset_index().rename(columns={'Sold by':'employee','Bill Amount':'total'} )
    res['incentive_amount'] = (res['total'] * 0.01).round(2)
    res = res[['employee','incentive_amount']].sort_values('incentive_amount', ascending=False)
    return res

# ============================================================================
# TAB 4: BOOKING MANAGEMENT
# ============================================================================

def get_booking_kpis(df):
    if df is None or df.empty:
        return pd.DataFrame({'total_today':[0], 'confirmed_today':[0], 'pending':[0], 'this_week':[0]})
    df2 = df.copy()
    df2['Appointment Date'] = safe_datetime_convert(df2, ['Appointment Date'])
    today = pd.Timestamp.now().normalize()
    week_later = today + timedelta(days=7)
    total_today = int(df2[df2['Appointment Date'].dt.normalize() == today].shape[0])
    confirmed_today = int(df2[(df2['Appointment Date'].dt.normalize() == today) & (df2['Status'] == 'Confirmed')].shape[0]) if 'Status' in df2.columns else 0
    pending = int(df2[df2['Status'] == 'Pending'].shape[0]) if 'Status' in df2.columns else 0
    this_week = int(df2[(df2['Appointment Date'] >= today) & (df2['Appointment Date'] <= week_later)].shape[0])
    return pd.DataFrame({'total_today':[total_today], 'confirmed_today':[confirmed_today], 'pending':[pending], 'this_week':[this_week]})

def get_bookings_by_date(df, target_date):
    if df is None or df.empty:
        return pd.DataFrame()
    df2 = df.copy()
    df2['Appointment Date'] = safe_datetime_convert(df2, ['Appointment Date'])
    t = pd.to_datetime(target_date).normalize()
    res = df2[df2['Appointment Date'].dt.normalize() == t]
    if 'Time Slot' in res.columns:
        try:
            res = res.sort_values('Time Slot')
        except Exception:
            pass
    return res

def get_monthly_booking_heatmap(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=['date','booking_count'])
    df2 = df.copy()
    df2['Appointment Date'] = safe_datetime_convert(df2, ['Appointment Date'])
    now = pd.Timestamp.now()
    df_month = df2[(df2['Appointment Date'].dt.month == now.month) & (df2['Appointment Date'].dt.year == now.year)].copy()
    if df_month.empty:
        return pd.DataFrame(columns=['date','booking_count'])
    df_month['date'] = df_month['Appointment Date'].dt.date
    res = df_month.groupby('date').size().reset_index(name='booking_count').sort_values('date')
    return res

def search_bookings(df, name=None, phone=None, service=None, employee=None):
    if df is None or df.empty:
        return pd.DataFrame()
    df2 = df.copy()
    if name:
        df2 = df2[df2['Name'].astype(str).str.contains(name, case=False, na=False)]
    if phone:
        df2 = df2[df2['Phone Number'].astype(str).str.contains(str(phone), case=False, na=False)]
    if service and service != "All":
        df2 = df2[df2['Service Booked'] == service]
    if employee and employee != "All":
        df2 = df2[df2['Preferred Employee'] == employee]
    if 'Appointment Date' in df2.columns:
        df2['Appointment Date'] = safe_datetime_convert(df2, ['Appointment Date'])
        df2 = df2.sort_values(['Appointment Date','Time Slot'], ascending=[False, True])
    return df2

# ============================================================================
# TAB 5: STAFF MANAGEMENT
# ============================================================================

def get_staff_kpis(staff_df, leave_df):
    if staff_df is None:
        staff_df = pd.DataFrame()
    total_staff = int(len(staff_df))
    active_staff = int(staff_df[staff_df.get('Status')=='Active'].shape[0]) if not staff_df.empty else 0
    # leaves
    if leave_df is None or leave_df.empty:
        on_leave_today = 0
    else:
        ld = leave_df.copy()
        ld['From Date'] = safe_datetime_convert(ld, ['From Date'])
        ld['To Date'] = safe_datetime_convert(ld, ['To Date'])
        today = pd.Timestamp.now().date()
        mask = (ld['From Date'].dt.date <= today) & (ld['To Date'].dt.date >= today) & (ld.get('Status') == 'Approved')
        on_leave_today = int(ld.loc[mask, 'Staff Name'].nunique()) if 'Staff Name' in ld.columns else 0
    # new this month
    if staff_df is None or staff_df.empty:
        new_this_month = 0
    else:
        s = staff_df.copy()
        s['Joining Date'] = safe_datetime_convert(s, ['Joining Date'])
        first_day = pd.Timestamp.now().replace(day=1)
        new_this_month = int(s[s['Joining Date'] >= first_day].shape[0])
    return {"total_staff": total_staff, "active_staff": active_staff, "on_leave_today": on_leave_today, "new_this_month": new_this_month}
def get_staff_attendance_stats(df):
    df2 = df.copy()
    df2["Date"] = pd.to_datetime(df2["Date"], errors="coerce")

    result = df2.groupby("Staff Name").agg(
        total_days=("Status", "count"),
        present_days=("Status", lambda x: (x == "Present").sum())
    ).reset_index()

    result["attendance_pct"] = round(
        (result["present_days"] / result["total_days"]) * 100, 2
    )

    return result


def get_upcoming_leaves(leave_df):
    if leave_df is None or leave_df.empty:
        return pd.DataFrame()
    df2 = leave_df.copy()
    df2['From Date'] = safe_datetime_convert(df2, ['From Date'])
    today = pd.Timestamp.now().normalize()
    res = df2[(df2['From Date'] >= today) & (df2.get('Status') == 'Approved')].sort_values('From Date')
    return res

def get_leave_calendar_data(leave_df):
    if leave_df is None or leave_df.empty:
        return pd.DataFrame()
    approved = leave_df[leave_df.get('Status') == 'Approved'].copy()
    if approved.empty:
        return pd.DataFrame()
    approved['From Date'] = safe_datetime_convert(approved, ['From Date'])
    approved['To Date'] = safe_datetime_convert(approved, ['To Date'])
    leave_days = []
    for _, row in approved.iterrows():
        if pd.isna(row['From Date']) or pd.isna(row['To Date']):
            continue
        rng = pd.date_range(row['From Date'].date(), row['To Date'].date())
        for d in rng:
            leave_days.append({"Date": d.date(), "Staff": row.get('Staff Name')})
    if not leave_days:
        return pd.DataFrame()
    ldf = pd.DataFrame(leave_days)
    res = ldf.groupby('Date').size().reset_index(name='leave_count').sort_values('Date')
    res = res.rename(columns={'Date':'date'})
    return res

def search_staff(staff_df, name=None, role=None, branch=None, status=None):
    if staff_df is None or staff_df.empty:
        return pd.DataFrame()
    df2 = staff_df.copy()
    if name:
        df2 = df2[df2['Name'].astype(str).str.contains(name, case=False, na=False)]
    if role and role != "All":
        df2 = df2[df2['Role'] == role]
    if branch and branch != "All":
        df2 = df2[df2['Branch'] == branch]
    if status and status != "All":
        df2 = df2[df2['Status'] == status]
    if 'Joining Date' in df2.columns:
        df2['Joining Date'] = safe_datetime_convert(df2, ['Joining Date'])
        df2 = df2.sort_values('Joining Date', ascending=False)
    return df2

