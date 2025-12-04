# booking_tab.py
"""
Premium Booking Management Tab for BLSH Dashboard
Handles appointment booking, scheduling, and calendar management
"""

import streamlit as st
import pandas as pd
import duckdb
from datetime import datetime, timedelta, time
import plotly.express as px
import plotly.graph_objects as go
from colors import Colors, get_kpi_card_style, get_status_badge_style

# ========== DATA LOADING ==========

@st.cache_data(ttl=60)
def load_appointments():
    """Load appointments data"""
    try:
        df = pd.read_csv("appointments.csv")
        df["Appointment Date"] = pd.to_datetime(df["Appointment Date"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Appointment ID", "Name", "Phone Number", "Service Booked",
            "Preferred Employee", "Appointment Date", "Time Slot", 
            "Duration", "Status", "Source"
        ])

@st.cache_data
def load_services():
    """Load services catalog"""
    try:
        return pd.read_csv("services.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Service Name", "Duration", "Price"])

@st.cache_data
def load_employees():
    """Load employees data"""
    try:
        return pd.read_csv("employees.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Employee Name", "Role", "Available"])


# ========== BOOKING LOGIC ==========

def check_overlap(employee, date, time_slot, duration, exclude_id=None):
    """Check if employee has overlapping bookings"""
    df = load_appointments()
    
    # Filter for same employee and date
    df_filtered = df[
        (df["Preferred Employee"] == employee) &
        (df["Appointment Date"] == pd.to_datetime(date)) &
        (df["Status"].isin(["Confirmed", "Pending"]))
    ]
    
    if exclude_id:
        df_filtered = df_filtered[df_filtered["Appointment ID"] != exclude_id]
    
    if df_filtered.empty:
        return False
    
    # Parse time
    req_hour, req_min = map(int, time_slot.split(":"))
    req_start = timedelta(hours=req_hour, minutes=req_min)
    req_end = req_start + timedelta(minutes=duration)
    
    # Check each existing booking
    for _, row in df_filtered.iterrows():
        exist_hour, exist_min = map(int, row["Time Slot"].split(":"))
        exist_start = timedelta(hours=exist_hour, minutes=exist_min)
        exist_end = exist_start + timedelta(minutes=row["Duration"])
        
        # Check overlap
        if req_start < exist_end and req_end > exist_start:
            return True
    
    return False


def get_available_slots(employee, date, duration):
    """Get available time slots for employee on given date"""
    all_slots = []
    start_hour, end_hour = 9, 20  # Salon hours
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            slot = f"{hour:02d}:{minute:02d}"
            if not check_overlap(employee, date, slot, duration):
                all_slots.append(slot)
    
    return all_slots


def save_booking(data):
    """Save new booking to CSV"""
    df = load_appointments()
    
    # Generate new ID
    if df.empty:
        new_id = "APT1000"
    else:
        last_id = int(df["Appointment ID"].str.replace("APT", "").max())
        new_id = f"APT{last_id + 1}"
    
    data["Appointment ID"] = new_id
    
    # Append to dataframe
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save to CSV
    df.to_csv("appointments.csv", index=False)
    st.cache_data.clear()
    
    return new_id


def update_booking(appointment_id, data):
    """Update existing booking"""
    df = load_appointments()
    
    # Update row
    idx = df[df["Appointment ID"] == appointment_id].index[0]
    for key, value in data.items():
        df.at[idx, key] = value
    
    # Save to CSV
    df.to_csv("appointments.csv", index=False)
    st.cache_data.clear()


def cancel_booking(appointment_id):
    """Cancel booking by setting status to Cancelled"""
    df = load_appointments()
    df.loc[df["Appointment ID"] == appointment_id, "Status"] = "Cancelled"
    df.to_csv("appointments.csv", index=False)
    st.cache_data.clear()


# ========== UI COMPONENTS ==========

def render_kpi_metrics():
    """Display booking KPIs"""
    df = load_appointments()
    today = pd.Timestamp.now().date()
    
    # Calculate metrics
    total_today = len(df[df["Appointment Date"].dt.date == today])
    confirmed_today = len(df[
        (df["Appointment Date"].dt.date == today) & 
        (df["Status"] == "Confirmed")
    ])
    pending = len(df[df["Status"] == "Pending"])
    this_week = len(df[
        (df["Appointment Date"] >= pd.Timestamp.now()) &
        (df["Appointment Date"] <= pd.Timestamp.now() + timedelta(days=7))
    ])
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    Today's Bookings
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.TEXT_PRIMARY};">
                    {total_today}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    Confirmed Today
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.DEEP_SAPPHIRE};">
                    {confirmed_today}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    Pending Confirmation
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.SOFT_TEAL};">
                    {pending}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    This Week
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.ROYAL_GOLD};">
                    {this_week}
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_booking_form():
    """Render new booking form"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>📅 New Booking</h3>", 
                unsafe_allow_html=True)
    
    services_df = load_services()
    employees_df = load_employees()
    
    with st.form("new_booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Customer Name*")
            phone = st.text_input("Phone Number*")
            service = st.selectbox("Select Service*", services_df["Service Name"].tolist())
            
        with col2:
            # Auto-load duration
            selected_service = services_df[services_df["Service Name"] == service]
            duration = selected_service["Duration"].values[0] if not selected_service.empty else 30
            st.text_input("Duration (minutes)", value=str(duration), disabled=True)
            
            employee = st.selectbox("Preferred Employee*", 
                                   employees_df["Employee Name"].tolist())
            date = st.date_input("Appointment Date*", 
                                min_value=datetime.now().date())
        
        # Get available slots
        available_slots = get_available_slots(employee, date, duration)
        
        col3, col4 = st.columns(2)
        with col3:
            if available_slots:
                time_slot = st.selectbox("Time Slot*", available_slots)
            else:
                st.warning("⚠️ No available slots for selected date/employee")
                time_slot = None
        
        with col4:
            source = st.selectbox("Booking Source*", 
                                 ["Walk-in", "Phone", "Instagram", "WhatsApp", "Website"])
        
        submit = st.form_submit_button("✅ Confirm Booking", use_container_width=True)
        
        if submit:
            if not all([customer_name, phone, time_slot]):
                st.error("❌ Please fill all required fields")
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
                
                new_id = save_booking(booking_data)
                st.success(f"✅ Booking confirmed! ID: {new_id}")
                st.rerun()


def render_bookings_table(selected_date):
    """Render bookings table for selected date"""
    df = load_appointments()
    
    # Filter by date
    df_filtered = df[df["Appointment Date"].dt.date == selected_date]
    df_filtered = df_filtered.sort_values("Time Slot")
    
    if df_filtered.empty:
        st.info("📭 No bookings for this date")
        return
    
    # Display table
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>📋 Bookings for {selected_date}</h3>", 
                unsafe_allow_html=True)
    
    for idx, row in df_filtered.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1, 1.5, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{row['Name']}**")
            st.caption(row['Phone Number'])
        
        with col2:
            st.markdown(f"🕐 {row['Time Slot']}")
            st.caption(f"{row['Duration']} min")
        
        with col3:
            st.markdown(f"💇 {row['Service Booked']}")
        
        with col4:
            st.markdown(f"👤 {row['Preferred Employee']}")
        
        with col5:
            st.markdown(get_status_badge_style(row['Status']), unsafe_allow_html=True)
        
        with col6:
            if row['Status'] not in ['Cancelled', 'Completed']:
                if st.button("✏️", key=f"edit_{row['Appointment ID']}"):
                    st.session_state.edit_id = row['Appointment ID']
                
                if st.button("❌", key=f"cancel_{row['Appointment ID']}"):
                    cancel_booking(row['Appointment ID'])
                    st.success("Booking cancelled")
                    st.rerun()
        
        st.divider()


def render_search_panel():
    """Render search and filter panel"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>🔍 Search Bookings</h3>", 
                unsafe_allow_html=True)
    
    df = load_appointments()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_name = st.text_input("Search by Name")
    with col2:
        search_phone = st.text_input("Search by Phone")
    with col3:
        search_service = st.selectbox("Filter by Service", 
                                     ["All"] + df["Service Booked"].unique().tolist())
    with col4:
        search_employee = st.selectbox("Filter by Employee", 
                                      ["All"] + df["Preferred Employee"].unique().tolist())
    
    # Apply filters
    filtered = df.copy()
    
    if search_name:
        filtered = filtered[filtered["Name"].str.contains(search_name, case=False, na=False)]
    
    if search_phone:
        filtered = filtered[filtered["Phone Number"].str.contains(search_phone, na=False)]
    
    if search_service != "All":
        filtered = filtered[filtered["Service Booked"] == search_service]
    
    if search_employee != "All":
        filtered = filtered[filtered["Preferred Employee"] == search_employee]
    
    # Display results
    if not filtered.empty:
        st.dataframe(
            filtered[[
                "Appointment ID", "Name", "Phone Number", "Service Booked",
                "Preferred Employee", "Appointment Date", "Time Slot", "Status"
            ]].sort_values("Appointment Date", ascending=False),
            use_container_width=True,
            height=300
        )
    else:
        st.info("No results found")


def render_calendar_view():
    """Render monthly calendar heatmap"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>📅 Monthly Calendar View</h3>", 
                unsafe_allow_html=True)
    
    df = load_appointments()
    
    # Get current month data
    today = pd.Timestamp.now()
    df_month = df[
        (df["Appointment Date"].dt.month == today.month) &
        (df["Appointment Date"].dt.year == today.year)
    ]
    
    # Count bookings per day
    daily_counts = df_month.groupby(df_month["Appointment Date"].dt.date).size().reset_index()
    daily_counts.columns = ["Date", "Bookings"]
    
    # Create heatmap
    fig = px.density_heatmap(
        daily_counts,
        x=pd.to_datetime(daily_counts["Date"]).dt.day,
        y=pd.to_datetime(daily_counts["Date"]).dt.day_name(),
        z="Bookings",
        color_continuous_scale=[Colors.BG_CARD, Colors.DEEP_SAPPHIRE, Colors.ROYAL_GOLD],
        labels={"x": "Day of Month", "y": "Day of Week", "z": "Bookings"}
    )
    
    fig.update_layout(
        paper_bgcolor=Colors.BG_DARK,
        plot_bgcolor=Colors.BG_CARD,
        font={"color": Colors.TEXT_PRIMARY},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_employee_timeline():
    """Render employee schedule timeline"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>👥 Employee Schedule Timeline</h3>", 
                unsafe_allow_html=True)
    
    df = load_appointments()
    today = pd.Timestamp.now().date()
    
    # Filter today's bookings
    df_today = df[
        (df["Appointment Date"].dt.date == today) &
        (df["Status"].isin(["Confirmed", "Pending"]))
    ].copy()
    
    if df_today.empty:
        st.info("No bookings scheduled for today")
        return
    
    # Create timeline data
    timeline_data = []
    for _, row in df_today.iterrows():
        hour, minute = map(int, row["Time Slot"].split(":"))
        start_time = datetime.combine(today, time(hour, minute))
        end_time = start_time + timedelta(minutes=row["Duration"])
        
        timeline_data.append({
            "Employee": row["Preferred Employee"],
            "Start": start_time,
            "End": end_time,
            "Service": row["Service Booked"],
            "Customer": row["Name"]
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Create Gantt chart
    fig = px.timeline(
        timeline_df,
        x_start="Start",
        x_end="End",
        y="Employee",
        color="Service",
        hover_data=["Customer"],
        color_discrete_sequence=Colors.CHART_PALETTE
    )
    
    fig.update_layout(
        paper_bgcolor=Colors.BG_DARK,
        plot_bgcolor=Colors.BG_CARD,
        font={"color": Colors.TEXT_PRIMARY},
        xaxis_title="Time",
        yaxis_title="Employee",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ========== MAIN BOOKING TAB ==========

def booking_tab():
    """Main booking tab function"""
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>📅 Booking Management</h1>", 
                unsafe_allow_html=True)
    
    # KPI Metrics
    render_kpi_metrics()
    st.divider()
    
    # Booking Form
    render_booking_form()
    st.divider()
    
    # Calendar Views
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_calendar_view()
    
    with col2:
        render_employee_timeline()
    
    st.divider()
    
    # Date Selection for Table View
    selected_date = st.date_input("Select Date to View Bookings", 
                                   value=datetime.now().date())
    render_bookings_table(selected_date)
    
    st.divider()
    
    # Search Panel
    render_search_panel()