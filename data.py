# generate_sample_data.py
"""
Generate sample CSV files for BLSH Dashboard demo
Run this script once to create all required data files
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_service_data():
    """Generate service_data.csv"""
    services = ["Waxing", "Facial", "De-tan", "Pedicure", "Manicure", 
                "Bleaching", "Wash", "Massage", "Threading", "Hair Cut"]
    employees = ["Priya", "Sneha", "Anjali", "Kavita", "Ritu"]
    payment_modes = ["Cash", "Card", "UPI", "Wallet"]
    helpers = ["Helper1", "Helper2", "Helper3", ""]
    
    data = []
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(500):
        timestamp = start_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(9, 20),
            minutes=random.randint(0, 59)
        )
        
        name = random.choice([
            "Anjali Sharma", "Priya Patel", "Neha Singh", "Kavita Reddy",
            "Sneha Gupta", "Ritu Mehta", "Pooja Desai", "Simran Kaur",
            "Aditi Joshi", "Divya Rao", "Sakshi Kumar", "Nisha Verma"
        ])
        
        phone = f"+91 {''.join([str(random.randint(0, 9)) for _ in range(10)])}"
        
        # Random services (1-3 services per visit)
        selected_services = random.sample(services, random.randint(1, 3))
        service_dict = {s: (s in selected_services) for s in services}
        
        bill_amount = sum([random.randint(200, 800) for _ in selected_services])
        
        data.append({
            "Bill Date & Time": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "Timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "Name": name,
            "Phone Number": phone,
            "Waxing": service_dict["Waxing"],
            "Facial": service_dict["Facial"],
            "De-tan": service_dict["De-tan"],
            "Pedicure": service_dict["Pedicure"],
            "Manicure": service_dict["Manicure"],
            "Bleaching": service_dict["Bleaching"],
            "Wash": service_dict["Wash"],
            "Massage": service_dict["Massage"],
            "Threading": service_dict["Threading"],
            "Hair Cut": service_dict["Hair Cut"],
            "Miscellaneous": "",
            "Bill Amount": bill_amount,
            "Service done by": random.choice(employees),
            "Payment Mode": random.choice(payment_modes),
            "Helper for S": random.choice(helpers),
            "Bill Date": timestamp.strftime("%d/%m/%Y"),
            "week": timestamp.isocalendar()[1],
            "Name of the day": timestamp.strftime("%A")
        })
    
    df = pd.DataFrame(data)
    df.to_csv("service_data.csv", index=False)
    print("✅ service_data.csv created with 500 records")


def generate_product_data():
    """Generate product_data.csv"""
    products = [
        "L'Oreal Hair Serum", "Lakme Face Cream", "Matrix Shampoo",
        "Biotique Face Pack", "VLCC Hair Oil", "Garnier Face Wash",
        "Revlon Lipstick", "Maybelline Mascara", "Dove Soap",
        "Neutrogena Sunscreen", "Plum Body Lotion", "Himalaya Neem Face Pack"
    ]
    
    employees = ["Priya", "Sneha", "Anjali", "Kavita", "Ritu"]
    payment_modes = ["Cash", "Card", "UPI", "Wallet"]
    helpers = ["Helper1", "Helper2", "Helper3", ""]
    
    data = []
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(200):
        timestamp = start_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(9, 20),
            minutes=random.randint(0, 59)
        )
        
        name = random.choice([
            "Anjali Sharma", "Priya Patel", "Neha Singh", "Kavita Reddy",
            "Sneha Gupta", "Ritu Mehta", "Pooja Desai", "Simran Kaur"
        ])
        
        phone = f"+91 {''.join([str(random.randint(0, 9)) for _ in range(10)])}"
        
        data.append({
            "Timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "DateTime": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "Client Name": name,
            "Client Number": phone,
            "Sold by": random.choice(employees),
            "Product Name": random.choice(products),
            "Bill Amount": random.randint(200, 1500),
            "Payment Mode": random.choice(payment_modes),
            "Helper": random.choice(helpers)
        })
    
    df = pd.DataFrame(data)
    df.to_csv("product_data.csv", index=False)
    print("✅ product_data.csv created with 200 records")


def generate_appointment_data():
    """Generate appointments.csv"""
    services = ["Waxing", "Facial", "De-tan", "Pedicure", "Manicure", 
                "Bleaching", "Hair Cut", "Threading", "Full Body Massage"]
    employees = ["Priya", "Sneha", "Anjali", "Kavita", "Ritu"]
    statuses = ["Confirmed", "Completed", "Cancelled", "Pending"]
    sources = ["Walk-in", "Phone", "Instagram", "WhatsApp", "Website"]
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(150):
        appt_date = start_date + timedelta(days=random.randint(0, 60))
        hour = random.randint(9, 19)
        minute = random.choice([0, 30])
        time_slot = f"{hour:02d}:{minute:02d}"
        
        name = random.choice([
            "Anjali Sharma", "Priya Patel", "Neha Singh", "Kavita Reddy",
            "Sneha Gupta", "Ritu Mehta", "Pooja Desai", "Simran Kaur",
            "Aditi Joshi", "Divya Rao"
        ])
        
        phone = f"+91{''.join([str(random.randint(0, 9)) for _ in range(10)])}"
        service = random.choice(services)
        duration = random.choice([30, 45, 60, 90])
        
        # Status logic: past = completed/cancelled, future = confirmed/pending
        if appt_date < datetime.now():
            status = random.choice(["Completed", "Cancelled"])
        else:
            status = random.choice(["Confirmed", "Pending"])
        
        data.append({
            "Appointment ID": f"APT{1000+i}",
            "Name": name,
            "Phone Number": phone,
            "Service Booked": service,
            "Preferred Employee": random.choice(employees),
            "Appointment Date": appt_date.strftime("%Y-%m-%d"),
            "Time Slot": time_slot,
            "Duration": duration,
            "Status": status,
            "Source": random.choice(sources)
        })
    
    df = pd.DataFrame(data)
    df.to_csv("appointments.csv", index=False)
    print("✅ appointments.csv created with 150 records")


def generate_services_csv():
    """Generate services.csv (service catalog)"""
    data = [
        {"Service Name": "Waxing", "Duration": 45, "Price": 500},
        {"Service Name": "Facial", "Duration": 60, "Price": 800},
        {"Service Name": "De-tan", "Duration": 30, "Price": 400},
        {"Service Name": "Pedicure", "Duration": 45, "Price": 600},
        {"Service Name": "Manicure", "Duration": 30, "Price": 400},
        {"Service Name": "Bleaching", "Duration": 45, "Price": 500},
        {"Service Name": "Hair Cut", "Duration": 30, "Price": 300},
        {"Service Name": "Wash", "Duration": 20, "Price": 200},
        {"Service Name": "Massage", "Duration": 60, "Price": 1000},
        {"Service Name": "Threading", "Duration": 15, "Price": 150},
        {"Service Name": "Full Body Massage", "Duration": 90, "Price": 1500},
    ]
    df = pd.DataFrame(data)
    df.to_csv("services.csv", index=False)
    print("✅ services.csv created")


def generate_employees_csv():
    """Generate employees.csv"""
    data = [
        {"Employee Name": "Priya", "Role": "Senior Stylist", "Available": True},
        {"Employee Name": "Sneha", "Role": "Beautician", "Available": True},
        {"Employee Name": "Anjali", "Role": "Hair Specialist", "Available": True},
        {"Employee Name": "Kavita", "Role": "Nail Technician", "Available": True},
        {"Employee Name": "Ritu", "Role": "Massage Therapist", "Available": True},
    ]
    df = pd.DataFrame(data)
    df.to_csv("employees.csv", index=False)
    print("✅ employees.csv created")


def generate_staff_csv():
    """Generate staff.csv for Staff Management tab"""
    data = [
        {
            "Staff ID": "STF001",
            "Name": "Priya Sharma",
            "Role": "Senior Stylist",
            "Phone": "+919876543210",
            "Email": "priya@blsh.com",
            "Joining Date": "2022-01-15",
            "Status": "Active",
            "Salary": 35000,
            "Branch": "Main Branch"
        },
        {
            "Staff ID": "STF002",
            "Name": "Sneha Patel",
            "Role": "Beautician",
            "Phone": "+919876543211",
            "Email": "sneha@blsh.com",
            "Joining Date": "2022-03-20",
            "Status": "Active",
            "Salary": 30000,
            "Branch": "Main Branch"
        },
        {
            "Staff ID": "STF003",
            "Name": "Anjali Singh",
            "Role": "Hair Specialist",
            "Phone": "+919876543212",
            "Email": "anjali@blsh.com",
            "Joining Date": "2023-01-10",
            "Status": "Active",
            "Salary": 32000,
            "Branch": "Branch 2"
        },
        {
            "Staff ID": "STF004",
            "Name": "Kavita Reddy",
            "Role": "Nail Technician",
            "Phone": "+919876543213",
            "Email": "kavita@blsh.com",
            "Joining Date": "2023-06-01",
            "Status": "Active",
            "Salary": 28000,
            "Branch": "Main Branch"
        },
        {
            "Staff ID": "STF005",
            "Name": "Ritu Mehta",
            "Role": "Massage Therapist",
            "Phone": "+919876543214",
            "Email": "ritu@blsh.com",
            "Joining Date": "2023-08-15",
            "Status": "Active",
            "Salary": 30000,
            "Branch": "Branch 2"
        },
    ]
    df = pd.DataFrame(data)
    df.to_csv("staff.csv", index=False)
    print("✅ staff.csv created")


def generate_leave_records_csv():
    """Generate leave_records.csv"""
    data = []
    start_date = datetime.now() - timedelta(days=60)
    staff_names = ["Priya Sharma", "Sneha Patel", "Anjali Singh", "Kavita Reddy", "Ritu Mehta"]
    leave_types = ["Sick Leave", "Casual Leave", "Vacation", "Personal"]
    
    for i in range(20):
        from_date = start_date + timedelta(days=random.randint(0, 90))
        to_date = from_date + timedelta(days=random.randint(1, 5))
        
        data.append({
            "Leave ID": f"LV{1000+i}",
            "Staff Name": random.choice(staff_names),
            "Leave Type": random.choice(leave_types),
            "From Date": from_date.strftime("%Y-%m-%d"),
            "To Date": to_date.strftime("%Y-%m-%d"),
            "Status": random.choice(["Approved", "Pending", "Rejected"]),
            "Remarks": random.choice(["Family function", "Medical", "Personal work", ""])
        })
    
    df = pd.DataFrame(data)
    df.to_csv("leave_records.csv", index=False)
    print("✅ leave_records.csv created")


def generate_attendance_csv():
    """Generate attendance.csv"""
    data = []
    start_date = datetime.now() - timedelta(days=90)
    staff_names = ["Priya Sharma", "Sneha Patel", "Anjali Singh", "Kavita Reddy", "Ritu Mehta"]
    
    for staff in staff_names:
        for day in range(90):
            date = start_date + timedelta(days=day)
            # 90% attendance rate
            present = random.random() < 0.9
            
            data.append({
                "Staff Name": staff,
                "Date": date.strftime("%Y-%m-%d"),
                "Status": "Present" if present else "Absent",
                "Check In": f"{random.randint(9, 10)}:{random.randint(0, 59):02d}" if present else "",
                "Check Out": f"{random.randint(18, 20)}:{random.randint(0, 59):02d}" if present else ""
            })
    
    df = pd.DataFrame(data)
    df.to_csv("attendance.csv", index=False)
    print("✅ attendance.csv created")


def generate_branches_csv():
    """Generate branches.csv"""
    data = [
        {"Branch ID": "BR001", "Branch Name": "Main Branch", "Location": "MG Road", "Manager": "Priya Sharma"},
        {"Branch ID": "BR002", "Branch Name": "Branch 2", "Location": "Koramangala", "Manager": "Anjali Singh"},
    ]
    df = pd.DataFrame(data)
    df.to_csv("branches.csv", index=False)
    print("✅ branches.csv created")


if __name__ == "__main__":
    print("🚀 Generating sample data for BLSH Dashboard...\n")
    
    generate_service_data()
    generate_product_data()
    generate_appointment_data()
    generate_services_csv()
    generate_employees_csv()
    generate_staff_csv()
    generate_leave_records_csv()
    generate_attendance_csv()
    generate_branches_csv()
    
    print("\n✨ All sample data files created successfully!")
    print("\n📁 Files created:")
    print("   - service_data.csv")
    print("   - product_data.csv")
    print("   - appointments.csv")
    print("   - services.csv")
    print("   - employees.csv")
    print("   - staff.csv")
    print("   - leave_records.csv")
    print("   - attendance.csv")
    print("   - branches.csv")