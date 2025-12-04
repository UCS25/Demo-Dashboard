# app.py - BLSH Dashboard (complete)
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import query
import plots
from colors import Colors, get_kpi_card_style, get_status_badge_style

st.set_page_config(page_title="Dashboard", layout="wide")

# Basic CSS (keeps your look)
st.markdown(f"""
 <style>
 .main {{
 background-color: {Colors.MIDNIGHT_BLACK};
}}
 .stTabs [data-baseweb="tab-list"] {{
 gap: 8px;
}}
 .stTabs [data-baseweb="tab"] {{
 background-color: {Colors.BG_CARD};
 border-radius: 8px;
 color: {Colors.TEXT_PRIMARY};
 padding: 8px 16px;
}}
 .stTabs [aria-selected="true"] {{
 background-color: {Colors.ROYAL_GOLD};
 color: {Colors.MIDNIGHT_BLACK};
}}
 </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=60)
def load_csv(filename):
    try:
        df = pd.read_csv(f"data/{filename}")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

def save_csv(df, filename):
    try:
        df.to_csv(f"data/{filename}", index=False)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False

# ============================================================================
# HELPERS
# ============================================================================

def safe_value(df, col):
    if df is None:
        return 0
    # df might be a dict or pandas Series or DataFrame
    try:
        if isinstance(df, dict):
            return df.get(col, 0)
        if isinstance(df, pd.Series):
            return df.get(col, 0)
        if isinstance(df, pd.DataFrame):
            return df[col].iloc[0] if col in df.columns and not df.empty else 0
    except Exception:
        return 0

def kpi_box(title, value):
    st.markdown(
        f"""
        <div style="{get_kpi_card_style()}">
          <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY};
                      text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
            {title}
          </div>
          <div style="font-size: 22px; font-weight: 600; color: {Colors.TEXT_PRIMARY};">
            {value}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# TABS
# ============================================================================

tabs = st.tabs([
    "Home",
    "Service Data",
    "Product Data",
    "Booking Management",
    "Staff Management"
])

# ============================================================================
# HOME TAB
# ============================================================================

with tabs[0]:
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>🏠 Home Dashboard</h1>", unsafe_allow_html=True)

    service_df = load_csv("service_data.csv")
    service_df = query.preprocess_data(service_df)

    if service_df.empty:
        st.warning("No service data found.")
    else:
        st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>Performance Indicators - Service</h3>", unsafe_allow_html=True)
        sales_today = safe_value(query.today_sales(service_df), "total_sales_today")
        customers_today = safe_value(query.today_customer_count(service_df), "customers_today")
        new_clients, repeated_clients = query.new_and_repeated_clients(service_df)
        total_services = safe_value(query.total_service_count(service_df), "total_services")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            kpi_box("Today's Sales", f"₹{sales_today:,.2f}")
        with col2:
            kpi_box("Customers Today", f"{int(customers_today)}")
        with col3:
            kpi_box("New Clients", f"{int(new_clients)}")
        with col4:
            kpi_box("Repeated Clients", f"{int(repeated_clients)}")
        with col5:
            kpi_box("Total Services", f"{int(total_services)}")

        st.divider()

        weekly_sales = safe_value(query.weekly_service_sales(service_df), "weekly_sales")
        weekly_count = safe_value(query.weekly_service_count(service_df), "weekly_service_count")
        monthly_sales = safe_value(query.monthly_service_sales(service_df), "monthly_sales")
        monthly_count = safe_value(query.monthly_service_count(service_df), "monthly_service_count")

        col6, col7, col8, col9 = st.columns(4)
        with col6:
            kpi_box("Weekly Sales", f"₹{weekly_sales:,.2f}")
        with col7:
            kpi_box("Weekly Visits", f"{int(weekly_count)}")
        with col8:
            kpi_box("Monthly Sales", f"₹{monthly_sales:,.2f}")
        with col9:
            kpi_box("Monthly Visits", f"{int(monthly_count)}")

        st.divider()

        prev_week_sales = safe_value(query.prev_week_service_sales(service_df), "prev_week_sales")
        prev_week_count = safe_value(query.prev_week_service_count(service_df), "prev_week_service_count")
        prev_month_sales = safe_value(query.prev_month_service_sales(service_df), "prev_month_sales")
        prev_month_count = safe_value(query.prev_month_service_count(service_df), "prev_month_service_count")

        col10, col11, col12, col13 = st.columns(4)
        with col10:
            kpi_box("Prev Week Sales", f"₹{prev_week_sales:,.2f}")
        with col11:
            kpi_box("Prev Week Visits", f"{int(prev_week_count)}")
        with col12:
            kpi_box("Prev Month Sales", f"₹{prev_month_sales:,.2f}")
        with col13:
            kpi_box("Prev Month Visits", f"{int(prev_month_count)}")

    # Product KPIs
    st.divider()
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>Product Sales Overview</h3>", unsafe_allow_html=True)
    product_df = load_csv("product_data.csv")
    product_df = query.preprocess_data(product_df)

    if product_df.empty:
        st.info("No product data found.")
    else:
        revenue_summary = query.get_revenue_summary(product_df)
        total_product_sales = revenue_summary.get("total_revenue", 0.0)
        total_products_sold = revenue_summary.get("total_sales", 0)
        products_today = safe_value(query.products_sold_today(product_df), "products_sold_today")
        products_week = safe_value(query.products_sold_last_week(product_df), "products_sold_last_week")
        products_month = safe_value(query.products_sold_last_month(product_df), "products_sold_last_month")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            kpi_box("Total Product Revenue", f"₹{total_product_sales:,.2f}")
        with col2:
            kpi_box("Total Products Sold", f"{int(total_products_sold)}")
        with col3:
            kpi_box("Products Sold Today", f"{int(products_today)}")
        with col4:
            kpi_box("Products Sold Last Week", f"{int(products_week)}")
        with col5:
            kpi_box("Products Sold Last Month", f"{int(products_month)}")

# ============================================================================
# SERVICE DATA TAB
# ============================================================================

with tabs[1]:
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>💇‍♀️ Service Data Dashboard</h1>", unsafe_allow_html=True)
    df = load_csv("service_data.csv")
    df = query.preprocess_data(df)
    if df.empty:
        st.warning("No service data found.")
    else:
        sales = query.cumulative_sales(df)
        month_sales = safe_value(sales, "month_sales")
        year_sales = safe_value(sales, "year_sales")
        col1, col2 = st.columns(2)
        col1.metric("Current Month Sales", f"₹{month_sales:,.2f}")
        col2.metric("Year-to-Date Sales", f"₹{year_sales:,.2f}")

        st.divider()
        st.subheader(" Incentive Table (1% of Total Bill)")
        incentive_df = query.incentive_table(df).reset_index(drop=True)
        if not incentive_df.empty:
            incentive_df.index = incentive_df.index + 1
            st.dataframe(incentive_df, use_container_width=True, height=250)
        else:
            st.info("No incentive data available")

        st.subheader(" Weekly Performance (Past 3 Months)")
        month_options = ["All months"] + sorted(df.get("Month", pd.Series()).dropna().unique().tolist())
        selected_month = st.selectbox("Select Month", month_options)
        performance_df = query.performance_table(df, selected_month).reset_index(drop=True)
        if not performance_df.empty:
            performance_df.index = performance_df.index + 1
            st.dataframe(performance_df, use_container_width=True, height=250)
        else:
            st.info("No performance data")

        st.subheader("Peak Customer Arrival Times")
        plots.plot_peak_hours(query.peak_hours(df))

        st.subheader("Customer Visits by Weekday")
        plots.plot_weekday_visit_counts(query.weekday_visit_counts(df))

        st.subheader("Service Count by Type")
        selected_month_service = st.selectbox("Select Month for Service Count", month_options, key="service_month")
        plots.plot_service_counts(query.service_count(df, selected_month_service))

        st.subheader("Top 20 Clients: Spending and Visits")
        top_clients_df = query.top_clients_spend_visits(df)
        if not top_clients_df.empty:
            top_clients_df.index = top_clients_df.index + 1
            st.dataframe(top_clients_df, use_container_width=True, height=400)
        else:
            st.info("No top clients data")

        st.subheader("Least 20 Clients: Spending and Visits")
        least_clients_df = query.least_clients_spend_visits(df)
        if not least_clients_df.empty:
            least_clients_df.index = least_clients_df.index + 1
            st.dataframe(least_clients_df, use_container_width=True, height=400)
        else:
            st.info("No least clients data")

        st.subheader("Customer Spend vs Visit Ratio")
        plots.plot_spend_vs_visits(query.spend_vs_visits(df))

        st.subheader("Days Since Last Visit")
        days_df = query.days_since_last_visit(df)
        if not days_df.empty:
            days_df.index = days_df.index + 1
            st.dataframe(days_df, use_container_width=True, height=400)
        else:
            st.info("No last-visit data")

        plots.plot_employee_performance(query.employee_service_ranking(df), query.employee_revenue_ranking(df))

        st.subheader("Unique Service Counts")
        selected_month_unique = st.selectbox("Select Month for Unique Service", month_options, key="unique_month")
        unique_service_df = query.unique_service_counts(df, selected_month_unique)
        if not unique_service_df.empty:
            unique_service_df.index = unique_service_df.index + 1
            st.dataframe(unique_service_df, use_container_width=True, height=250)
        else:
            st.info("No service-count data")

# ============================================================================
# PRODUCT DATA TAB
# ============================================================================

with tabs[2]:
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>📦 Product Sales Insights</h1>", unsafe_allow_html=True)
    pdf = load_csv("product_data.csv")
    pdf = query.preprocess_data(pdf)
    if pdf.empty:
        st.warning("No product data found.")
    else:
        revenue_summary = query.get_revenue_summary(pdf)
        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"₹{revenue_summary['total_revenue']:.2f}")
        col2.metric("Total Sales", f"{int(revenue_summary['total_sales'])}")
        plots.plot_incentive_by_employee(query.get_incentive_by_employee(pdf))
        plots.plot_employee_sales(query.get_employee_sales(pdf))
        plots.plot_employee_revenue(query.get_employee_revenue(pdf))
        plots.plot_top_products(query.get_top_products(pdf))
        plots.plot_sales_by_day(query.get_sales_by_day(pdf))

# ============================================================================
# BOOKING MANAGEMENT TAB
# ============================================================================

with tabs[3]:
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>Booking Management</h1>", unsafe_allow_html=True)
    appointments_df = load_csv("appointments.csv")
    services_df = load_csv("services.csv")
    employees_df = load_csv("employees.csv")

    if not appointments_df.empty:
        # ensure Appointment Date parsed
        appointments_df['Appointment Date'] = pd.to_datetime(appointments_df['Appointment Date'], errors='coerce')
        kpis = query.get_booking_kpis(appointments_df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            kpi_box("Today's Bookings", f"{safe_value(kpis,'total_today')}")
        with col2:
            kpi_box("Confirmed Today", f"{safe_value(kpis,'confirmed_today')}")
        with col3:
            kpi_box("Pending", f"{safe_value(kpis,'pending')}")
        with col4:
            kpi_box("This Week", f"{safe_value(kpis,'this_week')}")
    else:
        st.info("No appointments data")

    st.divider()
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>New Booking</h3>", unsafe_allow_html=True)


    def check_overlap(appts, employee, date, time_slot, duration, exclude_id=None):
        if appts is None or appts.empty:
            return False
        appts_copy = appts.copy()
        appts_copy['Appointment Date'] = pd.to_datetime(appts_copy['Appointment Date'], errors='coerce')
        filtered = appts_copy[(appts_copy.get('Preferred Employee') == employee) & (appts_copy['Appointment Date'].dt.date == pd.to_datetime(date).date()) & (appts_copy.get('Status').isin(['Confirmed','Pending']))]
        if exclude_id:
            filtered = filtered[filtered['Appointment ID'] != exclude_id]
        if filtered.empty:
            return False
        req_h, req_m = map(int, time_slot.split(':'))
        req_start = req_h*60 + req_m
        req_end = req_start + int(duration)
        for _, row in filtered.iterrows():
            try:
                exist_h, exist_m = map(int, str(row.get('Time Slot','00:00')).split(':'))
            except Exception:
                continue
            exist_start = exist_h*60 + exist_m
            exist_end = exist_start + int(row.get('Duration',30))
            if req_start < exist_end and req_end > exist_start:
                return True
        return False

    def get_available_slots(appointments_df, employee, date, duration):
        all_slots = []
        start_hour, end_hour = 9, 20
        for hour in range(start_hour, end_hour):
            for minute in [0,30]:
                slot = f"{hour:02d}:{minute:02d}"
                if not check_overlap(appointments_df, employee, date, slot, duration):
                    all_slots.append(slot)
        return all_slots

    def save_booking(appointments_df, data):
        ap = appointments_df.copy() if appointments_df is not None else pd.DataFrame()
        if ap.empty:
            new_id = "APT1000"
        else:
            try:
                last_id = max(int(str(x).replace("APT","")) for x in ap["Appointment ID"].astype(str).tolist() if str(x).startswith("APT"))
                new_id = f"APT{last_id+1}"
            except Exception:
                new_id = "APT1000"
        data["Appointment ID"] = new_id
        new_row = pd.DataFrame([data])
        ap2 = pd.concat([ap, new_row], ignore_index=True)
        save_csv(ap2, "appointments.csv")
        return new_id

    # Booking form
    with st.form("new_booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name*")
            phone = st.text_input("Phone Number*")
            service = st.selectbox("Select Service*", services_df["Service Name"].tolist() if not services_df.empty else [])
        with col2:
            selected_service = services_df[services_df["Service Name"] == service] if not services_df.empty else pd.DataFrame()
            duration = int(selected_service["Duration"].values[0]) if not selected_service.empty else 30
            employee = st.selectbox("Preferred Employee*", employees_df["Employee Name"].tolist() if not employees_df.empty else [])
            date = st.date_input("Appointment Date*", min_value=datetime.now().date())
            available_slots = get_available_slots(appointments_df, employee, date, duration)
            if available_slots:
                time_slot = st.selectbox("Time Slot*", available_slots)
            else:
                time_slot = None
            source = st.selectbox("Booking Source*", ["Walk-in","Phone","Instagram","WhatsApp","Website"])
        submit = st.form_submit_button("✅ Confirm Booking")
        if submit:
            if not all([customer_name, phone, time_slot]):
                st.error("Please fill required fields")
            else:
                booking_data = {
                    "Name": customer_name,
                    "Phone Number": phone,
                    "Service Booked": service,
                    "Preferred Employee": employee,
                    "Appointment Date": date.strftime("%Y-%m-%d"),
                    "Time Slot": time_slot,
                    "Duration": duration,
                    "Status": "Confirmed",
                    "Source": source
                }
                new_id = save_booking(appointments_df, booking_data)
                st.success(f"Booking confirmed! ID: {new_id}")
                st.rerun()

    st.divider()
    # Calendar & Today's schedule
    if not appointments_df.empty:
        heatmap_data = query.get_monthly_booking_heatmap(appointments_df)
        plots.plot_monthly_calendar_heatmap(heatmap_data)
        today = pd.Timestamp.now().date()
        today_bookings = query.get_bookings_by_date(appointments_df, today)
        plots.plot_employee_timeline(today_bookings, today)
    else:
        st.info("No appointments to show calendar/today schedule.")

    st.divider()
    # Bookings table and search
    selected_date = st.date_input("Select Date to View Bookings", value=datetime.now().date())
    if not appointments_df.empty:
        date_bookings = query.get_bookings_by_date(appointments_df, selected_date)
        if not date_bookings.empty:
            st.dataframe(date_bookings.sort_values("Time Slot"), use_container_width=True)
        else:
            st.info("No bookings for this date")
    else:
        st.info("No bookings data")

    st.divider()
    st.markdown("🔍 Search Bookings")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_name = st.text_input("Search by Name")
    with col2:
        search_phone = st.text_input("Search by Phone")
    with col3:
        search_service = st.selectbox("Filter by Service", ["All"] + appointments_df.get("Service Booked", pd.Series()).dropna().unique().tolist() if not appointments_df.empty else ["All"])
    with col4:
        search_employee = st.selectbox("Filter by Employee", ["All"] + appointments_df.get("Preferred Employee", pd.Series()).dropna().unique().tolist() if not appointments_df.empty else ["All"])
    if not appointments_df.empty:
        filtered = query.search_bookings(appointments_df, search_name, search_phone, search_service, search_employee)
        if not filtered.empty:
            st.dataframe(filtered[["Appointment ID","Name","Phone Number","Service Booked","Preferred Employee","Appointment Date","Time Slot","Status"]], use_container_width=True)
        else:
            st.info("No results found")

# ============================================================================
# STAFF MANAGEMENT TAB
# ============================================================================

with tabs[4]:
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>👥 Staff Management</h1>", unsafe_allow_html=True)
    staff_df = load_csv("staff.csv")
    leave_df = load_csv("leave_records.csv")
    attendance_df = load_csv("attendance.csv")
    branches_df = load_csv("branches.csv")

    # Parse dates where applicable
    if not staff_df.empty and 'Joining Date' in staff_df.columns:
        staff_df['Joining Date'] = pd.to_datetime(staff_df['Joining Date'], errors='coerce')
    if not leave_df.empty:
        leave_df['From Date'] = pd.to_datetime(leave_df['From Date'], errors='coerce')
        leave_df['To Date'] = pd.to_datetime(leave_df['To Date'], errors='coerce')
    if not attendance_df.empty:
        attendance_df['Date'] = pd.to_datetime(attendance_df['Date'], errors='coerce')

    # KPIs
    kpis = query.get_staff_kpis(staff_df, leave_df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_box("Total Staff", f"{kpis['total_staff']}")
    with col2:
        kpi_box("Active Staff", f"{kpis['active_staff']}")
    with col3:
        kpi_box("On Leave Today", f"{kpis['on_leave_today']}")
    with col4:
        kpi_box("New This Month", f"{kpis['new_this_month']}")

    st.divider()
    st.markdown("👥 Staff Directory")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_name = st.text_input("Search by Name", key="staff_search")
    with col2:
        filter_role = st.selectbox("Filter by Role", ["All"] + staff_df.get("Role", pd.Series()).dropna().unique().tolist() if not staff_df.empty else ["All"])
    with col3:
        filter_branch = st.selectbox("Filter by Branch", ["All"] + staff_df.get("Branch", pd.Series()).dropna().unique().tolist() if not staff_df.empty else ["All"])
    with col4:
        filter_status = st.selectbox("Filter by Status", ["All"] + staff_df.get("Status", pd.Series()).dropna().unique().tolist() if not staff_df.empty else ["All"])

    if not staff_df.empty:
        filtered_staff = query.search_staff(staff_df, search_name if search_name else None, filter_role if filter_role != "All" else None, filter_branch if filter_branch != "All" else None, filter_status if filter_status != "All" else None)
        if not filtered_staff.empty:
            st.dataframe(filtered_staff[['Staff ID','Name','Role','Phone','Email','Joining Date','Status','Salary','Branch']], use_container_width=True)
        else:
            st.info("No staff found matching the filters")
    else:
        st.info("No staff data available")

    st.divider()
    st.markdown("📊 Attendance Statistics")
    if not attendance_df.empty:
        attendance_stats = query.get_staff_attendance_stats(attendance_df)
        if not attendance_stats.empty:
            plots.plot_attendance_by_staff(attendance_stats)
            st.markdown("### Detailed Attendance Report (Last 30 Days)")
            st.dataframe(attendance_stats, use_container_width=True)
        else:
            st.info("No attendance stats")
    else:
        st.info("No attendance records found")

    st.divider()
    st.markdown("🗓️ Leave Management")
    if not leave_df.empty:
        upcoming_leaves = query.get_upcoming_leaves(leave_df)
        if not upcoming_leaves.empty:
            for idx, r in upcoming_leaves.head(10).iterrows():
                st.markdown(f"**{r.get('Staff Name','')}** — {r.get('Leave Type','')} — From {r.get('From Date')} To {r.get('To Date')}")
        else:
            st.info("No upcoming approved leaves")
        leave_calendar = query.get_leave_calendar_data(leave_df)
        plots.plot_leave_calendar_heatmap(leave_calendar)
    else:
        st.info("No leave records")

    st.divider()
    st.markdown("➕ Add New Staff")
    with st.form("add_staff_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name*")
            new_role = st.selectbox("Role*", ["Senior Stylist","Junior Stylist","Beautician","Receptionist","Manager","Helper"])
            new_phone = st.text_input("Phone Number*")
            new_email = st.text_input("Email*")
        with col2:
            new_branch = st.selectbox("Branch*", branches_df.get("Branch Name", ["Main Branch"]).tolist() if not branches_df.empty else ["Main Branch"])
            new_salary = st.number_input("Salary*", min_value=0, step=1000)
            new_joining = st.date_input("Joining Date*")
            new_status = st.selectbox("Status", ["Active","On Leave","Inactive"])
        submit_staff = st.form_submit_button("Add Staff Member")
        if submit_staff:
            if new_name and new_phone and new_email:
                s = staff_df.copy() if not staff_df.empty else pd.DataFrame()
                if s.empty:
                    new_id = "STF001"
                else:
                    try:
                        last_id = max(int(str(x).replace("STF","")) for x in s["Staff ID"].astype(str).tolist() if str(x).startswith("STF"))
                        new_id = f"STF{last_id+1:03d}"
                    except Exception:
                        new_id = "STF001"
                new_staff = pd.DataFrame([{
                    "Staff ID": new_id,
                    "Name": new_name,
                    "Role": new_role,
                    "Phone": new_phone,
                    "Email": new_email,
                    "Joining Date": new_joining.strftime("%Y-%m-%d"),
                    "Status": new_status,
                    "Salary": new_salary,
                    "Branch": new_branch
                }])
                staff_df2 = pd.concat([s, new_staff], ignore_index=True) if not s.empty else new_staff
                save_csv(staff_df2, "staff.csv")
                st.success(f"Staff member {new_name} added. ID: {new_id}")
                st.experimental_rerun()
            else:
                st.error("Please fill required fields")

    st.divider()
    st.markdown("✅ Mark Attendance")
    with st.form("mark_attendance_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            att_staff = st.selectbox("Staff Member*", staff_df[staff_df['Status']=='Active']['Name'].tolist() if not staff_df.empty else [])
        with col2:
            att_date = st.date_input("Date*", value=pd.Timestamp.now().date())
        with col3:
            att_status = st.selectbox("Status*", ["Present","Absent","Half Day","On Leave"])
        check_in = st.time_input("Check In Time", value=None) if att_status in ["Present","Half Day"] else None
        check_out = st.time_input("Check Out Time", value=None) if att_status in ["Present","Half Day"] else None
        submit_attendance = st.form_submit_button("Mark Attendance")
        if submit_attendance:
            if att_staff and att_date:
                a = attendance_df.copy() if not attendance_df.empty else pd.DataFrame()
                new_att = pd.DataFrame([{
                    "Staff Name": att_staff,
                    "Date": att_date.strftime("%Y-%m-%d"),
                    "Status": att_status,
                    "Check In": check_in.strftime("%H:%M") if check_in else "",
                    "Check Out": check_out.strftime("%H:%M") if check_out else ""
                }])
                a2 = pd.concat([a, new_att], ignore_index=True) if not a.empty else new_att
                save_csv(a2, "attendance.csv")
                st.success("Attendance marked")
                st.experimental_rerun()
            else:
                st.error("Please fill required fields")
