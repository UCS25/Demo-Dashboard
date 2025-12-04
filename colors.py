# colors.py
"""
Premium Business Color Palette for BLSH Dashboard
Consistent color scheme across all tabs and visualizations
"""

class Colors:
    # Primary Colors
    MIDNIGHT_BLACK = "#0D1117"
    PLATINUM_GRAY = "#C5C9CC"
    ROYAL_GOLD = "#D4AF37"
    DEEP_SAPPHIRE = "#1A4B84"
    SOFT_TEAL = "#3BA3A4"
    
    # Status Colors
    STATUS_CONFIRMED = DEEP_SAPPHIRE
    STATUS_CANCELLED = PLATINUM_GRAY
    STATUS_COMPLETED = ROYAL_GOLD
    STATUS_PENDING = SOFT_TEAL
    
    # Background Colors
    BG_DARK = "#161B22"
    BG_CARD = "rgba(240, 240, 240, 0.05)"
    BG_HOVER = "rgba(212, 175, 55, 0.1)"
    
    # Text Colors
    TEXT_PRIMARY = "rgba(230, 230, 230, 0.95)"
    TEXT_SECONDARY = "rgba(130, 130, 130, 0.9)"
    TEXT_MUTED = "rgba(100, 100, 100, 0.7)"
    
    # Border Colors
    BORDER_LIGHT = "rgba(128, 128, 128, 0.2)"
    BORDER_ACCENT = "rgba(212, 175, 55, 0.3)"
    
    # Chart Colors (for Plotly)
    CHART_PALETTE = [
        DEEP_SAPPHIRE,
        ROYAL_GOLD,
        SOFT_TEAL,
        PLATINUM_GRAY,
        "#2C5282",
        "#B8860B",
        "#4FB3B4",
    ]
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Return color based on status"""
        status_map = {
            "confirmed": Colors.STATUS_CONFIRMED,
            "cancelled": Colors.STATUS_CANCELLED,
            "completed": Colors.STATUS_COMPLETED,
            "pending": Colors.STATUS_PENDING,
            "active": Colors.SOFT_TEAL,
            "resigned": Colors.PLATINUM_GRAY,
            "on leave": Colors.ROYAL_GOLD,
        }
        return status_map.get(status.lower(), Colors.PLATINUM_GRAY)
    
    @staticmethod
    def get_plotly_template():
        """Return Plotly template with custom colors"""
        return {
            "layout": {
                "paper_bgcolor": Colors.BG_DARK,
                "plot_bgcolor": Colors.BG_CARD,
                "font": {"color": Colors.TEXT_PRIMARY},
                "colorway": Colors.CHART_PALETTE,
            }
        }


def get_kpi_card_style():
    """Return consistent KPI card styling"""
    return f"""
        background-color: {Colors.BG_CARD};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {Colors.BORDER_LIGHT};
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    """


def get_section_header_style():
    """Return consistent section header styling"""
    return f"""
        color: {Colors.ROYAL_GOLD};
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid {Colors.BORDER_ACCENT};
    """


def get_status_badge_style(status: str):
    """Return status badge HTML"""
    color = Colors.get_status_color(status)
    return f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
        ">{status}</span>
    """