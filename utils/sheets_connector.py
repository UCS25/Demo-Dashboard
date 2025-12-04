# utils/sheets_connector.py
"""
CSV Data Connector for BLSH Dashboard
Replaces Google Sheets with local CSV files
"""

import pandas as pd
import streamlit as st
from pathlib import Path

# File mapping for backward compatibility
SHEET_FILE_MAP = {
    "Client Data": "service_data.csv",
    "Product Sale": "product_data.csv",
    "Appointments": "appointments.csv",
    "Services": "services.csv",
    "Employees": "employees.csv",
    "Staff": "staff.csv",
    "Leave Records": "leave_records.csv",
    "Attendance": "attendance.csv",
    "Branches": "branches.csv"
}

@st.cache_data(ttl=60)
def get_sheet_data(sheet_name):
    """
    Load data from CSV file
    
    Args:
        sheet_name: Name of the sheet/data source
        
    Returns:
        pandas.DataFrame: Loaded data
    """
    filename = SHEET_FILE_MAP.get(sheet_name, f"{sheet_name}.csv")
    
    try:
        # Try to load from current directory
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        # Try to load from data directory
        try:
            data_path = Path("data") / filename
            df = pd.read_csv(data_path)
            return df
        except FileNotFoundError:
            st.warning(f"⚠️ Data file not found: {filename}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading {filename}: {str(e)}")
        return pd.DataFrame()


def save_sheet_data(sheet_name, dataframe):
    """
    Save data back to CSV file
    
    Args:
        sheet_name: Name of the sheet/data source
        dataframe: pandas DataFrame to save
    """
    filename = SHEET_FILE_MAP.get(sheet_name, f"{sheet_name}.csv")
    
    try:
        # Try to save to current directory
        dataframe.to_csv(filename, index=False)
        st.cache_data.clear()
        return True
    except Exception as e:
        # Try to save to data directory
        try:
            data_path = Path("data") / filename
            data_path.parent.mkdir(exist_ok=True)
            dataframe.to_csv(data_path, index=False)
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"❌ Error saving {filename}: {str(e)}")
            return False


def list_available_sheets():
    """
    List all available data sources
    
    Returns:
        list: Names of available sheets
    """
    available = []
    
    for sheet_name in SHEET_FILE_MAP.keys():
        df = get_sheet_data(sheet_name)
        if not df.empty:
            available.append(sheet_name)
    
    return available


def get_sheet_info(sheet_name):
    """
    Get information about a sheet
    
    Args:
        sheet_name: Name of the sheet
        
    Returns:
        dict: Sheet information (rows, columns, size)
    """
    df = get_sheet_data(sheet_name)
    
    if df.empty:
        return None
    
    return {
        "name": sheet_name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
    }