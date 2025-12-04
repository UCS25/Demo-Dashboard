# staff_management_tab.py
"""
Premium Staff Management Tab for BLSH Dashboard
Handles staff directory, leave management, attendance, and performance
"""

import streamlit as st
import pandas as pd
import duckdb
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from colors import Colors, get_kpi_card_style, get_status_badge_style

# ========== DATA LOADING ==========

@st.cache_data(ttl=60)
def load_staff():
    """Load staff data"""
    try:
        df = pd.read_csv("staff.csv")
        df["Joining Date"] = pd.to_datetime(df["Joining Date"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Staff ID", "Name", "Role", "Phone", "Email", 
            "Joining Date", "Status", "Salary", "Branch"
        ])

@st.cache_data(ttl=60)
def load_leave_records():
    """Load leave records"""
    try:
        df = pd.read_csv("leave_records.csv")
        df["From Date"] = pd.to_datetime(df["From Date"])
        df["To Date"] = pd.to_datetime(df["To Date"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Leave ID", "Staff Name", "Leave Type", "From Date", 
            "To Date", "Status", "Remarks"
        ])

@st.cache_data(ttl=60)
def load_attendance():
    """Load attendance data"""
    try:
        df = pd.read_csv("attendance.csv")
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Staff Name", "Date", "Status", "Check In", "Check Out"
        ])

@st.cache_data
def load_branches():
    """Load branches data"""
    try:
        return pd.read_csv("branches.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Branch ID", "Branch Name", "Location", "Manager"])


# ========== STAFF CRUD OPERATIONS ==========

def add_staff(data):
    """Add new staff member"""
    df = load_staff()
    
    # Generate new ID
    if df.empty:
        new_id = "STF001"
    else:
        last_num = int(df["Staff ID"].str.replace("STF", "").max())
        new_id = f"STF{str(last_num + 1).zfill(3)}"
    
    data["Staff ID"] = new_id
    
    # Append to dataframe
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save to CSV
    df.to_csv("staff.csv", index=False)
    st.cache_data.clear()
    
    return new_id


def update_staff(staff_id, data):
    """Update existing staff member"""
    df = load_staff()
    
    # Update row
    idx = df[df["Staff ID"] == staff_id].index[0]
    for key, value in data.items():
        df.at[idx, key] = value
    
    # Save to CSV
    df.to_csv("staff.csv", index=False)
    st.cache_data.clear()


def delete_staff(staff_id):
    """Soft delete staff by setting status to Resigned"""
    df = load_staff()
    df.loc[df["Staff ID"] == staff_id, "Status"] = "Resigned"
    df.to_csv("staff.csv", index=False)
    st.cache_data.clear()


def add_leave_record(data):
    """Add new leave record"""
    df = load_leave_records()
    
    # Generate new ID
    if df.empty:
        new_id = "LV1000"
    else:
        last_id = int(df["Leave ID"].str.replace("LV", "").max())
        new_id = f"LV{last_id + 1}"
    
    data["Leave ID"] = new_id
    data["Status"] = "Pending"
    
    # Append to dataframe
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save to CSV
    df.to_csv("leave_records.csv", index=False)
    st.cache_data.clear()
    
    return new_id


# ========== ANALYTICS QUERIES ==========

def get_staff_kpis():
    """Calculate staff KPIs"""
    staff_df = load_staff()
    leave_df = load_leave_records()
    today = pd.Timestamp.now().date()
    
    total_staff = len(staff_df)
    active_staff = len(staff_df[staff_df["Status"] == "Active"])
    
    # Staff on leave today
    on_leave_today = len(leave_df[
        (leave_df["From Date"].dt.date <= today) &
        (leave_df["To Date"].dt.date >= today) &
        (leave_df["Status"] == "Approved")
    ])
    
    # New staff this month
    this_month = today.replace(day=1)
    new_this_month = len(staff_df[
        staff_df["Joining Date"].dt.date >= this_month
    ])
    
    return {
        "total_staff": total_staff,
        "active_staff": active_staff,
        "on_leave_today": on_leave_today,
        "new_this_month": new_this_month
    }


def get_attendance_stats():
    """Calculate attendance statistics"""
    att_df = load_attendance()
    staff_df = load_staff()
    
    if att_df.empty or staff_df.empty:
        return pd.DataFrame()
    
    # Last 30 days
    thirty_days_ago = pd.Timestamp.now() - timedelta(days=30)
    att_df_recent = att_df[att_df["Date"] >= thirty_days_ago]
    
    query = """
        SELECT 
            "Staff Name",
            COUNT(*) as total_days,
            SUM(CASE WHEN Status = 'Present' THEN 1 ELSE 0 END) as present_days,
            ROUND(100.0 * SUM(CASE WHEN Status = 'Present' THEN 1 ELSE 0 END) / COUNT(*), 2) as attendance_pct
        FROM att_df_recent
        GROUP BY "Staff Name"
        ORDER BY attendance_pct DESC
    """
    
    return duckdb.query(query).df()


# ========== UI COMPONENTS ==========

def render_staff_kpis():
    """Display staff overview KPIs"""
    kpis = get_staff_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    Total Staff
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.TEXT_PRIMARY};">
                    {kpis['total_staff']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    Active Staff
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.SOFT_TEAL};">
                    {kpis['active_staff']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    On Leave Today
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.ROYAL_GOLD};">
                    {kpis['on_leave_today']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="{get_kpi_card_style()}">
                <div style="font-size: 13px; color: {Colors.TEXT_SECONDARY}; 
                            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    New This Month
                </div>
                <div style="font-size: 22px; font-weight: 600; color: {Colors.DEEP_SAPPHIRE};">
                    {kpis['new_this_month']}
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_staff_directory():
    """Display staff directory with search and filters"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>👥 Staff Directory</h3>", 
                unsafe_allow_html=True)
    
    staff_df = load_staff()
    
    # Search and filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_name = st.text_input("Search by Name", key="staff_search_name")
    with col2:
        filter_role = st.selectbox("Filter by Role", 
                                   ["All"] + staff_df["Role"].unique().tolist(),
                                   key="staff_filter_role")
    with col3:
        filter_branch = st.selectbox("Filter by Branch", 
                                    ["All"] + staff_df["Branch"].unique().tolist(),
                                    key="staff_filter_branch")
    with col4:
        filter_status = st.selectbox("Filter by Status", 
                                    ["All"] + staff_df["Status"].unique().tolist(),
                                    key="staff_filter_status")
    
    # Apply filters
    filtered = staff_df.copy()
    
    if search_name:
        filtered = filtered[filtered["Name"].str.contains(search_name, case=False, na=False)]
    
    if filter_role != "All":
        filtered = filtered[filtered["Role"] == filter_role]
    
    if filter_branch != "All":
        filtered = filtered[filtered["Branch"] == filter_branch]
    
    if filter_status != "All":
        filtered = filtered[filtered["Status"] == filter_status]
    
    # Display table
    if not filtered.empty:
        for idx, row in filtered.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 1])
            
            with col1:
                st.markdown(f"**{row['Name']}**")
                st.caption(f"📧 {row['Email']}")
            
            with col2:
                st.markdown(f"**{row['Role']}**")
                st.caption(f"📞 {row['Phone']}")
            
            with col3:
                st.markdown(f"🏢 {row['Branch']}")
                st.caption(f"💰 ₹{row['Salary']:,.0f}")
            
            with col4:
                st.markdown(get_status_badge_style(row['Status']), unsafe_allow_html=True)
            
            with col5:
                if st.button("✏️", key=f"edit_staff_{row['Staff ID']}"):
                    st.session_state.edit_staff_id = row['Staff ID']
                
                if row['Status'] != 'Resigned':
                    if st.button("🗑️", key=f"delete_staff_{row['Staff ID']}"):
                        delete_staff(row['Staff ID'])
                        st.success("Staff resigned")
                        st.rerun()
            
            st.divider()
    else:
        st.info("No staff members found")


def render_add_staff_form():
    """Render add new staff form"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>➕ Add New Staff</h3>", 
                unsafe_allow_html=True)
    
    branches_df = load_branches()
    roles = ["Senior Stylist", "Beautician", "Hair Specialist", "Nail Technician", 
             "Massage Therapist", "Receptionist", "Manager"]
    
    with st.form("add_staff_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*")
            role = st.selectbox("Role*", roles)
            phone = st.text_input("Phone*")
            email = st.text_input("Email*")
        
        with col2:
            salary = st.number_input("Salary*", min_value=0, step=1000)
            joining_date = st.date_input("Joining Date*", value=datetime.now())
            status = st.selectbox("Status*", ["Active", "On Leave", "Resigned"])
            branch = st.selectbox("Branch*", branches_df["Branch Name"].tolist())
        
        submit = st.form_submit_button("✅ Add Staff", use_container_width=True)
        
        if submit:
            if not all([name, role, phone, email]):
                st.error("❌ Please fill all required fields")
            else:
                staff_data = {
                    "Name": name,
                    "Role": role,
                    "Phone": phone,
                    "Email": email,
                    "Joining Date": joining_date.strftime("%Y-%m-%d"),
                    "Status": status,
                    "Salary": salary,
                    "Branch": branch
                }
                
                new_id = add_staff(staff_data)
                st.success(f"✅ Staff added successfully! ID: {new_id}")
                st.rerun()


def render_leave_management():
    """Render leave management panel"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>🏖️ Leave Management</h3>", 
                unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Apply Leave", "Leave Calendar", "Upcoming Leaves"])
    
    with tab1:
        render_apply_leave_form()
    
    with tab2:
        render_leave_calendar()
    
    with tab3:
        render_upcoming_leaves()


def render_apply_leave_form():
    """Render leave application form"""
    staff_df = load_staff()
    active_staff = staff_df[staff_df["Status"] == "Active"]
    
    with st.form("apply_leave_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            staff_name = st.selectbox("Staff Name*", active_staff["Name"].tolist())
            leave_type = st.selectbox("Leave Type*", 
                                     ["Sick Leave", "Casual Leave", "Vacation", "Personal", "Other"])
            from_date = st.date_input("From Date*", min_value=datetime.now().date())
        
        with col2:
            to_date = st.date_input("To Date*", min_value=datetime.now().date())
            remarks = st.text_area("Remarks")
        
        submit = st.form_submit_button("📝 Submit Leave Application", use_container_width=True)
        
        if submit:
            if to_date < from_date:
                st.error("❌ To Date must be after From Date")
            else:
                leave_data = {
                    "Staff Name": staff_name,
                    "Leave Type": leave_type,
                    "From Date": from_date.strftime("%Y-%m-%d"),
                    "To Date": to_date.strftime("%Y-%m-%d"),
                    "Remarks": remarks
                }
                
                new_id = add_leave_record(leave_data)
                st.success(f"✅ Leave application submitted! ID: {new_id}")
                st.rerun()


def render_leave_calendar():
    """Render leave calendar heatmap"""
    leave_df = load_leave_records()
    
    if leave_df.empty:
        st.info("No leave records found")
        return
    
    # Filter approved leaves
    approved_leaves = leave_df[leave_df["Status"] == "Approved"]
    
    # Expand date ranges to individual days
    leave_days = []
    for _, row in approved_leaves.iterrows():
        date_range = pd.date_range(row["From Date"], row["To Date"])
        for date in date_range:
            leave_days.append({"Date": date, "Staff": row["Staff Name"]})
    
    if not leave_days:
        st.info("No approved leaves found")
        return
    
    leave_days_df = pd.DataFrame(leave_days)
    
    # Count leaves per day
    daily_counts = leave_days_df.groupby(leave_days_df["Date"].dt.date).size().reset_index()
    daily_counts.columns = ["Date", "Leave Count"]
    
    # Create heatmap
    fig = px.density_heatmap(
        daily_counts,
        x=pd.to_datetime(daily_counts["Date"]).dt.day,
        y=pd.to_datetime(daily_counts["Date"]).dt.day_name(),
        z="Leave Count",
        color_continuous_scale=[Colors.BG_CARD, Colors.SOFT_TEAL, Colors.ROYAL_GOLD],
        labels={"x": "Day of Month", "y": "Day of Week", "z": "Leaves"}
    )
    
    fig.update_layout(
        paper_bgcolor=Colors.BG_DARK,
        plot_bgcolor=Colors.BG_CARD,
        font={"color": Colors.TEXT_PRIMARY},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_upcoming_leaves():
    """Display upcoming leave records"""
    leave_df = load_leave_records()
    today = pd.Timestamp.now()
    
    # Filter future leaves
    upcoming = leave_df[
        (leave_df["From Date"] >= today) &
        (leave_df["Status"] == "Approved")
    ].sort_values("From Date")
    
    if upcoming.empty:
        st.info("No upcoming leaves")
        return
    
    st.dataframe(
        upcoming[[
            "Leave ID", "Staff Name", "Leave Type", 
            "From Date", "To Date", "Remarks"
        ]],
        use_container_width=True,
        height=300
    )


def render_staff_performance():
    """Render staff performance dashboard"""
    st.markdown(f"<h3 style='color: {Colors.ROYAL_GOLD};'>📊 Staff Performance</h3>", 
                unsafe_allow_html=True)
    
    att_stats = get_attendance_stats()
    
    if att_stats.empty:
        st.info("No attendance data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average attendance
        avg_attendance = att_stats["attendance_pct"].mean()
        st.metric("Average Attendance %", f"{avg_attendance:.1f}%")
        
        # Top performer
        top_performer = att_stats.iloc[0]
        st.metric("Top Performing Staff", top_performer["Staff Name"],
                 delta=f"{top_performer['attendance_pct']:.1f}%")
    
    with col2:
        # Low attendance
        low_att_count = len(att_stats[att_stats["attendance_pct"] < 80])
        st.metric("Staff with Low Attendance (<80%)", low_att_count)
    
    # Bar chart: Staff-wise attendance
    st.markdown("#### Attendance by Staff (Last 30 Days)")
    fig = px.bar(
        att_stats,
        x="Staff Name",
        y="attendance_pct",
        text="attendance_pct",
        color="attendance_pct",
        color_continuous_scale=[Colors.PLATINUM_GRAY, Colors.SOFT_TEAL, Colors.ROYAL_GOLD]
    )
    
    fig.update_layout(
        paper_bgcolor=Colors.BG_DARK,
        plot_bgcolor=Colors.BG_CARD,
        font={"color": Colors.TEXT_PRIMARY},
        yaxis_title="Attendance %",
        xaxis_title="Staff Name",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ========== MAIN STAFF MANAGEMENT TAB ==========

def staff_management_tab():
    """Main staff management tab function"""
    st.markdown(f"<h1 style='color: {Colors.ROYAL_GOLD};'>👥 Staff Management</h1>", 
                unsafe_allow_html=True)
    
    # KPI Metrics
    render_staff_kpis()
    st.divider()
    
    # Staff Directory
    render_staff_directory()
    st.divider()
    
    # Add New Staff Form
    render_add_staff_form()
    st.divider()
    
    # Leave Management
    render_leave_management()
    st.divider()
    
    # Staff Performance
    render_staff_performance()