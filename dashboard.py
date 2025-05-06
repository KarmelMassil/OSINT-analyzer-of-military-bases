import streamlit as st
import json
import os
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import re
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from geopy.geocoders import Nominatim

# Set page configuration
st.set_page_config(
    page_title="Military Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for military-style theme
st.markdown("""
<style>
    .main {
        background-color: #1a2639;
        color: #e6e6e6;
    }
    .stApp {
        background-color: #1a2639;
    }
    /* Improved sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a2639;
        border-right: 1px solid #2a3f5f;
    }
    [data-testid="stSidebarNav"] {
        background-color: #1a2639;
    }
    .css-1d391kg, .css-1lcbmhc {
        background-color: #1a2639;
    }
    /* Sidebar elements */
    .stButton button {
        background-color: #2a3f5f;
        color: #64ffda;
        border: 1px solid #64ffda;
        transition: background-color 0.2s ease-in-out;
    }
    .stButton button:hover {
        background-color: #457b9d;
        color: #ffffff;
    }

    /* Ensure standard text is white */
    p, li, strong, label {
        color: #ffffff; /* Ensure standard text is white */
    }

    /* --- Dropdown Styling Fixes --- */
    /* Style for the closed selectbox display container */
    /* Targeting based on role="button" and data-baseweb="select" is more robust */
    .stSelectbox div[role="button"][data-baseweb="select"] {
        background-color: #2a3f5f !important; /* Dark background for closed box */
        border: 1px solid #457b9d !important; /* Border color */
        border-radius: 5px !important; /* Match other inputs */
        color: #d1d7e0 !important; /* Light text for closed box container */
    }

     /* Style for the actual text element inside the closed selectbox */
     /* Targeting the input[type="text"] within the container */
     .stSelectbox div[role="button"][data-baseweb="select"] input[type="text"] {
         background-color: #2a3f5f !important; /* Ensure background is dark */
         color: #d1d7e0 !important; /* Ensure text is light */
         -webkit-text-fill-color: #d1d7e0 !important; /* Handle autofill colors in webkit browsers */
         opacity: 1 !important; /* Ensure text is not hidden */
     }

     /* Style for the closed selectbox hover state */
     .stSelectbox div[role="button"][data-baseweb="select"]:hover {
         border-color: #64ffda !important;
     }

    /* Style for the dropdown menu (popover) */
    [data-baseweb="popover"] {
        background-color: #ffffff !important; /* White background for the dropdown list */
        color: #333333 !important; /* Default text color for popover content */
    }

    /* Style for the individual options within the dropdown menu */
    [data-baseweb="popover"] div[role="option"] {
        color: #333333 !important; /* Dark text for options */
        background-color: #ffffff !important; /* White background for options */
    }
    /* Style for hovered dropdown options */
     [data-baseweb="popover"] div[role="option"]:hover {
         background-color: #e9ecef !important; /* Light grey background on hover */
         color: #1a2639 !important; /* Darker text on hover */
     }

    /* Style for the options list container within the popover */
    [data-baseweb="popover"] > div > ul {
         background-color: #ffffff !important; /* Ensure the list background is white */
    }

    /* Ensure label text is visible (already present, keep) */
    /* Moved this rule down to ensure it applies correctly after general 'label' rule */
    .stSelectbox label {
        color: #d1d7e0 !important; /* Light text for the label */
        background-color: transparent !important;
    }
    /* --- End Dropdown Styling Fixes --- */

    .sidebar-menu-item {
        background-color: #2a3f5f;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #64ffda;
        color: #d1d7e0 !important; /* Ensure header text color is visible */
        font-weight: bold;
    }
     /* Ensure text within sidebar menu item is also visible */
    .sidebar-menu-item p {
        color: #d1d7e0 !important;
    }

    .title-container {
        background-color: #2a3f5f;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 5px solid #64ffda;
    }
    .dashboard-title {
        color: #ffffff !important; /* Changed to white and added !important */
        font-weight: bold;
        margin: 0;
    }
    .dashboard-subtitle {
        color: #d1d7e0;
        font-style: italic;
    }
    .section-header {
        background-color: #2a3f5f;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 5px solid #64ffda;
        color: #64ffda;
        font-weight: bold; /* Make section headers bold */
    }
    .card {
        background-color: #2a3f5f;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 3px solid #64ffda;
    }
    .card-title {
        color: #64ffda;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .key-metric {
        font-size: 1.5rem;
        font-weight: bold;
        color: #64ffda;
    }
    .metric-label {
        color: #d1d7e0;
        font-size: 0.85rem;
    }
    .analyst-report {
        background-color: #2a3f5f;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #457b9d;
        color: #ffffff;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #2a3f5f;
        color: #d1d7e0;
    }
    .status-critical {
        color: #ff5252;
        font-weight: bold;
    }
    .status-warning {
        color: #ffca28;
        font-weight: bold;
    }
    .status-secure {
        color: #4caf50;
        font-weight: bold;
    }
    .findings-list li {
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    /* Expander styling */
    .st-expander {
        background-color: #2a3f5f !important;
        border-radius: 5px !important;
        border: 1px solid #457b9d; /* Add a subtle border */
    }
    .st-expander div[data-testid="stExpanderHeader"] {
         background-color: #2a3f5f !important; /* Header background */
         color: #d1d7e0 !important; /* Header text color */
         font-weight: bold;
    }
     .st-expander div[data-testid="stExpanderHeader"] svg { /* Expander arrow color */
         fill: #d1d7e0 !important;
     }
    .st-expander div[data-testid="stExpanderContent"] {
         background-color: #1a2639 !important; /* Content background */
         color: #ffffff !important; /* Content text color */
    }

    /* Improve text readability with better contrast */
    /* Removed div from here as it was too broad and might conflict */
    p, li, strong, label {
        color: #ffffff; /* Ensure standard text is white */
    }


    /* Checkboxes styling */
    .stCheckbox label {
        color: #d1d7e0 !important; /* Label text color */
    }
    .stCheckbox > div[role="checkbox"] {
        background-color: #2a3f5f !important; /* Checkbox background */
        border: 1px solid #457b9d !important; /* Checkbox border */
    }
    .stCheckbox > div[role="checkbox"] svg { /* Checkmark color */
        color: #64ffda !important;
        fill: #64ffda !important;
    }
    /* Radio button styling */
    .stRadio > label {
         color: #d1d7e0 !important; /* Radio label color */
    }
    .stRadio div[role="radiogroup"] label {
         color: #ffffff !important; /* Individual radio option text color */
    }
     .stRadio div[role="radiogroup"] div[data-baseweb="radio"] svg { /* Radio button circle color */
         fill: #64ffda !important;
         color: #64ffda !important; /* Radio button circle inner color */
     }

     /* Text Input styling */
    .stTextInput > label {
        color: #d1d7e0 !important;
    }
    .stTextInput > div > input {
        background-color: #2a3f5f !important;
        color: #ffffff !important;
        border: 1px solid #457b9d !important;
        border-radius: 5px !important;
    }
    .stTextInput > div > input:focus {
        border-color: #64ffda !important;
        box-shadow: 0 0 0 0.2rem rgba(100, 255, 218, 0.25); /* Glow effect */
        outline: none !important;
    }

    /* Number Input styling */
    .stNumberInput > label {
        color: #d1d7e0 !important;
    }
    .stNumberInput > div > input {
         background-color: #2a3f5f !important;
         color: #ffffff !important;
         border: 1px solid #457b9d !important;
         border-radius: 5px !important;
    }
     .stNumberInput > div > input:focus {
        border-color: #64ffda !important;
        box-shadow: 0 0 0 0.2rem rgba(100, 255, 218, 0.25); /* Glow effect */
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)
# Header
st.markdown("""
<div class="title-container">
    <h1 class="dashboard-title">🛰️ STRATEGIC RECONNAISSANCE INTELLIGENCE DASHBOARD</h1>
    <p class="dashboard-subtitle">Classified Satellite Image Analysis of Foreign Military Facilities</p>
</div>
""", unsafe_allow_html=True)
# Load data function
@st.cache_data
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("data.json file not found. Please ensure the file exists in the current directory.")
        return {}
    except json.JSONDecodeError:
        st.error("Error parsing data.json. Please check the file format.")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred loading data: {e}")
        return {}

# Extract insights from analyst reports
def extract_insights(analyst_history):
    all_findings = []
    all_analyses = []

    if not isinstance(analyst_history, list):
        # Handle cases where analyst_history might not be a list
        return [], []

    for report in analyst_history:
        try:
            report_data = report
            # If report is a string, try parsing it as JSON
            if isinstance(report, str):
                report_data = json.loads(report)

            if isinstance(report_data, dict):
                 if "findings" in report_data:
                     findings = report_data["findings"]
                     if isinstance(findings, list):
                         all_findings.extend(findings)
                     elif isinstance(findings, str):
                          # Simple split by common separators like newlines or bullets
                          all_findings.extend([f.strip() for f in re.split(r'[\n*-]', findings) if f.strip()])


                 if "analysis" in report_data:
                      analysis = report_data["analysis"]
                      if isinstance(analysis, str):
                         all_analyses.append(analysis)
                      elif isinstance(analysis, list):
                          # If analysis is a list, join elements into a single string
                          all_analyses.append("\n".join([str(item) for item in analysis if item is not None]))


        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            # Skip invalid reports
            continue

    return all_findings, all_analyses

# Count frequencies of keywords in findings
def count_keywords(all_findings):
    keywords = {
        "runway": 0, "hangar": 0, "radar": 0, "missile": 0, "vehicle": 0,
        "building": 0, "bunker": 0, "compound": 0, "storage": 0, "facility": 0,
        "aircraft": 0, "defense": 0, "tower": 0, "tank": 0, "base": 0,
        "activity": 0, "personnel": 0, "equipment": 0, "weaponry": 0, "deployment": 0
    }

    for finding in all_findings:
        if isinstance(finding, str): # Ensure finding is a string
            finding_lower = finding.lower()
            for keyword in keywords:
                if keyword in finding_lower:
                    keywords[keyword] += 1

    # Convert to list of tuples for plotting
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords

# Get the screenshots for each location
def get_screenshots(base_name_number, country):
    screenshot_dir = "base_screenshots"
    screenshots = []

    if not os.path.exists(screenshot_dir):
        return []

    # Look for files that match Country_Base_X_(lat,lon)_loopY.png pattern
    # X is the base number extracted from the base_name
    if not isinstance(base_name_number, str) or not base_name_number:
        return []

    # Escape country and base_name_number for regex just in case they contain special characters
    escaped_country = re.escape(country.lower())
    escaped_base_number = re.escape(base_name_number.lower())

    # Inside get_screenshots function:
    # This regex pattern matches your file format: Country_Base_X_(lat,lon)_loopY.png
    # Modified regex to use .+? for coordinates to simplify pattern parsing
    search_pattern = rf"^{escaped_country}_base_{escaped_base_number}_loop\d+\.png$"

    try:
        all_files = os.listdir(screenshot_dir)
    except Exception as e:
        # Error listing directory
        return []


    for filename in all_files: # Loop through the listed files
        # Use regex to match the pattern case-insensitively
        if re.match(search_pattern, filename.lower()):
            screenshots.append(os.path.join(screenshot_dir, filename))


    # Sort files for consistency (e.g., loop1, loop2, etc.)
    screenshots.sort()

    return screenshots[:8]  # Return up to 8 screenshots

# Assign threat level to each base based on analysis (instead of randomly)
# Uses insights extracted from analyst_history
def assign_threat_levels(data):
    threat_levels = {}
    # Define keywords that indicate a higher threat presence
    high_threat_keywords = ["runway", "hangar", "radar", "missile", "vehicle",
        "building", "bunker", "compound", "storage", "facility",
        "aircraft", "defense", "tower", "tank", "base",
        "activity", "personnel", "equipment", "weaponry", "deployment"]

    # We will reuse the extract_insights and count_keywords functions already in the script
    # from . extract_insights, count_keywords # Assuming they are in the same file/module

    for loc_key, loc_data in data.items():
        threat_score = 0
        # Get insights (findings and analysis) from analyst history for this base
        analyst_history = loc_data.get('analyst_history', [])
        # We only need findings for the keyword count
        all_findings, _ = extract_insights(analyst_history)

        # Count keywords in the findings
        # count_keywords returns a list of (keyword, count) tuples
        keyword_counts_list = count_keywords(all_findings)

        # Convert the list of tuples to a dictionary for easier lookup
        keyword_dict = dict(keyword_counts_list)

        # Calculate the threat score based on the counts of high-threat keywords
        for keyword in high_threat_keywords:
            # Get the count for each high-threat keyword, default to 0 if not found
            threat_score += keyword_dict.get(keyword, 0)

        # Map the calculated threat score to a threat level
        threat_level = "LOW" # Default level
        if threat_score > 0: # If any high-threat keyword is found
             threat_level = "MODERATE"
        if threat_score >= 10: # If 3 or more total high-threat keywords
             threat_level = "HIGH"
        if threat_score >= 20: # If 6 or more total high-threat keywords (Adjust threshold as needed)
             threat_level = "CRITICAL"

        # Store the determined threat level for this base
        threat_levels[loc_key] = threat_level

    return threat_levels

# Haversine formula to calculate distance between two coordinates
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    except (ValueError, TypeError):
        # Return infinity if conversion fails
        return float('inf')


    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

# Find nearest threat location
def find_nearest_threat(data, threat_levels, current_lat, current_lon):
    nearest_distance = float('inf')
    nearest_base_name = None
    nearest_threat_level = None
    nearest_coords = None # To store coords of nearest base

    # Ensure current location is valid floats
    try:
        current_lat_float = float(current_lat) if current_lat is not None else None
        current_lon_float = float(current_lon) if current_lon is not None else None
        if current_lat_float is None or current_lon_float is None or (current_lat_float == 0.0 and current_lon_float == 0.0):
             return None, None, None, None
    except (ValueError, TypeError):
         return None, None, None, None


    for loc_key, loc_data in data.items():
        try:
            base_lat = float(loc_data.get('latitude', 0))
            base_lon = float(loc_data.get('longitude', 0))

            if base_lat == 0.0 and base_lon == 0.0:
                continue

            distance = haversine(current_lon_float, current_lat_float, base_lon, base_lat)

            # Consider only bases with threat level HIGH or CRITICAL as potential threats
            threat_level = threat_levels.get(loc_key, "UNKNOWN")
            if threat_level in ["HIGH", "CRITICAL"]:
                 if distance < nearest_distance:
                     nearest_distance = distance
                     nearest_base_name = loc_data.get('base_name')
                     nearest_threat_level = threat_level
                     nearest_coords = (base_lat, base_lon)

        except (ValueError, TypeError):
            continue # Skip locations with invalid coordinates

    # Return None if no threats found
    if nearest_base_name is None:
        return None, None, None, None

    return nearest_base_name, nearest_threat_level, nearest_distance, nearest_coords

# Location search using geocoding
# Removed @st.cache_data as geocoding results might change or service could have state
def get_location_coordinates(location_name):
    if not location_name:
         return None, None
    try:
        geolocator = Nominatim(user_agent="military_intelligence_dashboard")
        # Added a timeout
        location = geolocator.geocode(location_name, timeout=5)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        st.error(f"Error retrieving location coordinates: {e}")
        return None, None
# Main function
def main():
    # Load data
    data = load_data()

    if not data:
        st.warning("No data available to display.")
        return

    # Assign threat levels
    threat_levels = assign_threat_levels(data)

    # Sidebar
    st.sidebar.markdown('<div class="section-header">Intelligence Controls</div>', unsafe_allow_html=True)

    # Create a list of locations for the selectbox display
    locations_display = []
    location_display_to_key = {}
    # Keep track of the first key for initial state
    # first_loc_key = None # Not strictly needed if we initialize index to 0

    for loc_key, loc_data in data.items():
        # if first_loc_key is None:
        #     first_loc_key = loc_key # Not needed with index 0 init
        base_name = loc_data.get('base_name', 'Unknown Base')
        country = loc_data.get('country', 'Unknown Country')
        # threat = threat_levels.get(loc_key, "UNKNOWN") # Threat is not needed in display name

        # Construct the display name without the threat level
        display_name = f"{base_name} ({country})"

        locations_display.append(display_name)
        # We still map the display name to the original loc_key
        location_display_to_key[display_name] = loc_key

    # Handle case with no locations loaded
    if not locations_display:
         st.error("No location data found or processed.")
         return

    # --- Fix for selected location not staying selected (using index) ---
    # Initialize session state for the selected location index
    if 'selected_location_index' not in st.session_state:
        st.session_state.selected_location_index = 0 # Index of the first item

    # Determine the index to pre-select in the selectbox from session state
    current_index = st.session_state.selected_location_index
    # Ensure the index is valid if the list of locations changed or state is stale
    if current_index >= len(locations_display) or current_index < 0:
        current_index = 0 # Default to the first item
        st.session_state.selected_location_index = 0 # Reset state if invalid index

    # Location selector using the index parameter
    selected_location_display = st.sidebar.selectbox(
        "Select Target Location",
        options=locations_display,
        index=current_index, # Use the determined index from state
        key='location_select_box' # Unique key for this widget state
    )

    # Find the index of the newly selected display name and save it to state
    # This happens after the selectbox returns the selected value on rerun
    try:
        new_index = locations_display.index(selected_location_display)
        st.session_state.selected_location_index = new_index
    except ValueError:
        # This should ideally not happen if selected_location_display came from locations_display
        # Fallback to index 0 if for some reason it's not found (e.g., data error)
        st.session_state.selected_location_index = 0
    # --- End Fix for selected location ---


    # Get the data for the selected location using the mapping
    # Use the value returned by the selectbox to look up data
    selected_loc_key = location_display_to_key.get(selected_location_display)

    selected_loc_data = data.get(selected_loc_key)

    # Check if data is not a dictionary (includes None case)
    if not isinstance(selected_loc_data, dict):
        st.error(f"Error: Could not retrieve valid data for '{selected_location_display}'. Please check the data source.")
        return # Exit the main function if data is invalid

    # If the code reaches here, selected_loc_data should be a valid dictionary
    # The rest of the code using selected_loc_data should now work


    # Sidebar - additional filters and controls with improved styling (rest of sidebar code)
    st.sidebar.markdown('<div class="sidebar-menu-item">Analysis Filters</div>', unsafe_allow_html=True)
    show_findings = st.sidebar.checkbox("Show Detailed Findings", value=True, key='show_findings_checkbox')
    show_commander = st.sidebar.checkbox("Show Commander's Report", value=True, key='show_commander_checkbox')
    show_raw_data = st.sidebar.checkbox("Show Raw Analysis Data", value=False, key='show_raw_data_checkbox')

    # Map display options
    st.sidebar.markdown('<div class="sidebar-menu-item">Map Display Options</div>', unsafe_allow_html=True)
    show_all_bases = st.sidebar.checkbox("Show All Bases on Map", value=True, key='show_all_bases_checkbox')

    # Add a section for your location
    st.sidebar.markdown('<div class="sidebar-menu-item">Your Location</div>', unsafe_allow_html=True)
    location_input_method = st.sidebar.radio(
        "Set Your Location By:",
        ("Coordinates", "Address/Location Name"),
        key='location_input_method_radio' # Key for this radio button state
    )

    current_lat = None
    current_lon = None

    if location_input_method == "Coordinates":
        # Initialize coordinates in session state if not set
        # These keys were initialized in the __main__ block, but checked again for clarity
        if 'user_lat' not in st.session_state: st.session_state.user_lat = 0.0
        if 'user_lon' not in st.session_state: st.session_state.user_lon = 0.0

        current_lat = st.sidebar.number_input("Your Latitude", value=st.session_state.user_lat, format="%.6f", key='user_lat_input')
        current_lon = st.sidebar.number_input("Your Longitude", value=st.session_state.user_lon, format="%.6f", key='user_lon_input')

        # Update session state when inputs change
        st.session_state.user_lat = current_lat
        st.session_state.user_lon = current_lon

        # Clear previous geocoded location if switching to coordinates
        st.session_state.user_geo_lat = None
        st.session_state.user_geo_lon = None


    else: # Address/Location Name
        if 'user_location_name' not in st.session_state: st.session_state.user_location_name = ""
        if 'user_geo_lat' not in st.session_state: st.session_state.user_geo_lat = None
        if 'user_geo_lon' not in st.session_state: st.session_state.user_geo_lon = None


        location_name_input = st.sidebar.text_input("Enter Address or Location Name", value=st.session_state.user_location_name, key='user_location_name_input')

        # Update session state for the input box
        st.session_state.user_location_name = location_name_input

        # Clear coordinate inputs if switching to address
        st.session_state.user_lat = 0.0
        st.session_state.user_lon = 0.0


        if st.sidebar.button("Search Location", key='search_location_button'):
            if location_name_input:
                lat, lon = get_location_coordinates(location_name_input)
                if lat is not None and lon is not None:
                    st.session_state.user_geo_lat = float(lat) # Ensure float
                    st.session_state.user_geo_lon = float(lon) # Ensure float
                    st.sidebar.success(f"Location found at: {lat:.6f}, {lon:.6f}")
                else:
                    st.session_state.user_geo_lat = None
                    st.session_state.user_geo_lon = None
                    st.sidebar.error("Location not found. Please try a different search term.")
            else:
                 st.sidebar.warning("Please enter a location name.")

        # Use the geocoded coordinates if available from a previous search
        current_lat = st.session_state.user_geo_lat
        current_lon = st.session_state.user_geo_lon

        # Display geocoded coords if they exist
        if current_lat is not None and current_lon is not None:
             st.sidebar.write(f"Current Geocoded Location: {current_lat:.6f}, {current_lon:.6f}")


    # Add a classification notice
    st.sidebar.markdown("""
    <div style="background-color: #e63946; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-top: 20px;">
        <strong>TOP SECRET</strong><br>
        AUTHORIZED PERSONNEL ONLY
    </div>
    """, unsafe_allow_html=True)

    # Current time
    now = datetime.now()
    st.sidebar.markdown(f"### Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1: # <--- Content for the first column
        # Target Information
        selected_base_name_display = str(selected_loc_data.get('base_name', 'Unknown Base')).upper()
        st.markdown(f"<div class='section-header'>TARGET: {selected_base_name_display}</div>", unsafe_allow_html=True)

        loc_cols = st.columns(3)
        with loc_cols[0]:
            st.markdown(f"**Country:** {selected_loc_data.get('country', 'N/A')}")
        with loc_cols[1]:
            # Safely get latitude and display
            lat_val = selected_loc_data.get('latitude')
            if isinstance(lat_val, (int, float)):
                 st.markdown(f"**Latitude:** {lat_val:.6f}")
                 selected_lat_float = float(lat_val)
            else:
                 st.markdown(f"**Latitude:** N/A")
                 selected_lat_float = 0.0 # Use default 0 for map if invalid

        with loc_cols[2]:
             # Safely get longitude and display
            lon_val = selected_loc_data.get('longitude')
            if isinstance(lon_val, (int, float)):
                 st.markdown(f"**Longitude:** {lon_val:.6f}")
                 selected_lon_float = float(lon_val)
            else:
                 st.markdown(f"**Longitude:** N/A")
                 selected_lon_float = 0.0 # Use default 0 for map if invalid

        # Use the floats for map logic
        selected_lat = selected_lat_float
        selected_lon = selected_lon_float


        # Map
        st.markdown("<div class='section-header'>GEOSPATIAL POSITIONING</div>", unsafe_allow_html=True)

        # Determine map center and zoom based on selection and show_all_bases
        # Default center if selected location has invalid coords or showing all bases
        map_center = [0, 0]
        map_zoom = 2 # Start zoomed out for global view

        if not show_all_bases and (selected_lat != 0.0 or selected_lon != 0.0):
             # Center on selected base if not showing all and coords are valid
             map_center = [selected_lat, selected_lon]
             map_zoom = 14 # Zoom in on a single base

        # Create map
        m = folium.Map(location=map_center,
                       zoom_start=map_zoom,
                       tiles="CartoDB dark_matter")

        # Add markers for all bases if requested
        if show_all_bases:
            for loc_key, loc_data in data.items():
                try:
                    # Ensure we have valid numerical coordinates
                    lat = float(loc_data.get('latitude', 0))
                    lon = float(loc_data.get('longitude', 0))

                    # Skip if coordinates are invalid or missing
                    if lat == 0.0 and lon == 0.0:
                        continue

                    # Ensure variables are strings right before the f-string
                    base_name = str(loc_data.get('base_name', 'Unknown Base'))
                    country = str(loc_data.get('country', 'Unknown Country'))
                    threat = str(threat_levels.get(loc_key, "UNKNOWN"))

                    # Determine marker color based on threat level
                    color = "blue" # Default color
                    if threat == "LOW":
                        color = "green"
                    elif threat == "MODERATE":
                        color = "orange"
                    elif threat in ["HIGH", "CRITICAL"]: # Use red for high/critical
                        color = "red"

                    # popup_html uses HTML comments for the style comment
                    popup_html = f"""
                    <div style="font-family: Arial; width: 200px; color: #333333;"> <h4>{base_name}</h4>
                        <b>Country:</b> {country}<br>
                        <b>Threat Level:</b> {threat}<br>
                        <b>Coordinates:</b> {lat:.4f}, {lon:.4f}
                    </div>
                    """

                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{base_name} ({threat})",
                        icon=folium.Icon(color=color, icon="crosshairs", prefix="fa")
                    ).add_to(m)
                except (ValueError, TypeError) as e:
                    # Skip this marker if there's an error with coordinates or data
                    continue
        else:
            # Just add the selected base marker if coordinates are valid
            if selected_lat != 0.0 or selected_lon != 0.0:
                 threat = threat_levels.get(selected_loc_key, "UNKNOWN")
                 color = "blue"
                 if threat == "LOW": color = "green"
                 elif threat == "MODERATE": color = "orange"
                 elif threat in ["HIGH", "CRITICAL"]: color = "red"

                 # Ensure variables are strings before using in f-string
                 selected_base_name_str = str(selected_loc_data.get('base_name', 'Unknown Base'))
                 selected_country_str = str(selected_loc_data.get('country', 'Unknown Country'))
                 selected_threat_str = str(threat)

                 # popup_html uses HTML comments for the style comment
                 popup_html = f"""
                     <div style="font-family: Arial; width: 200px; color: #333333;"> <h4>{selected_base_name_str}</h4>
                         <b>Country:</b> {selected_country_str}<br>
                         <b>Threat Level:</b> {selected_threat_str}<br>
                         <b>Coordinates:</b> {selected_lat:.4f}, {selected_lon:.4f}
                     </div>
                     """
                 folium.Marker(
                     [selected_lat, selected_lon],
                     popup=folium.Popup(popup_html, max_width=300),
                     tooltip=selected_loc_data.get('base_name', 'Unknown Base'),
                     icon=folium.Icon(color=color, icon="crosshairs", prefix="fa")
                 ).add_to(m)


        # Add user's location marker if coordinates are provided and valid
        # Ensure current_lat/lon are floats for comparison
        try:
            current_lat_float = float(current_lat) if current_lat is not None else None
            current_lon_float = float(current_lon) if current_lon is not None else None
        except (ValueError, TypeError):
             current_lat_float = None
             current_lon_float = None


        if current_lat_float is not None and current_lon_float is not None and (current_lat_float != 0.0 or current_lon_float != 0.0):
            # Add user location marker
            folium.Marker(
                [current_lat_float, current_lon_float],
                popup="Your Location",
                tooltip="Your Location",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)

            # Find nearest threat (pass the potentially non-float original values to find_nearest_threat)
            nearest_base_name, nearest_threat, nearest_distance, nearest_coords = find_nearest_threat(
                 data, threat_levels, current_lat, current_lon)


            if nearest_base_name and nearest_coords:
                threat_lat, threat_lon = nearest_coords
                # Add a line connecting your location to the nearest threat
                folium.PolyLine(
                    locations=[[current_lat_float, current_lon_float], [threat_lat, threat_lon]],
                    color="#64ffda",
                    weight=2,
                    opacity=0.7,
                    dash_array="5"
                ).add_to(m)

                # Add distance info near the line midpoint
                mid_lat = (current_lat_float + threat_lat) / 2
                mid_lon = (current_lon_float + threat_lon) / 2

                folium.Marker(
                    [mid_lat, mid_lon],
                    popup=f"Distance: {nearest_distance:.1f} km",
                    tooltip=f"{nearest_distance:.1f} km",
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                            color: white;
                            background-color: rgba(42, 63, 95, 0.8);
                            padding: 3px 6px; /* Adjusted padding */
                            border: 1px solid #64ffda;
                            border-radius: 3px; /* Adjusted border-radius */
                            font-size: 10px;
                            font-weight: bold;
                            white-space: nowrap; /* Prevent text wrapping */
                        ">{nearest_distance:.1f} km</div>
                        """
                    )
                ).add_to(m)

        # Display map
        folium_static(m, width=700, height=450) # Adjusted map size slightly

        # Display nearest threat info if user location is provided and valid
        if current_lat_float is not None and current_lon_float is not None and (current_lat_float != 0.0 or current_lon_float != 0.0):
             # Re-call find_nearest_threat to get the info for display below the map
             nearest_base_name, nearest_threat, nearest_distance, _ = find_nearest_threat(
                 data, threat_levels, current_lat, current_lon) # Pass original current_lat/lon

             if nearest_base_name:
                 threat_color_class = {
                     "CRITICAL": "status-critical",
                     "HIGH": "status-critical",
                     "MODERATE": "status-warning",
                     "LOW": "status-secure",
                     "UNKNOWN": ""
                 }
                 st.markdown(f"""
                 <div class="card">
                     <div class="card-title">Proximity Alert</div>
                     <p><strong>Nearest Threat:</strong> {nearest_base_name}</p>
                     <p><strong>Threat Level:</strong> <span class="{threat_color_class.get(nearest_threat, '')}">{nearest_threat}</span></p>
                     <p><strong>Distance:</strong> {nearest_distance:.1f} km</p>
                 </div>
                 """, unsafe_allow_html=True)
             else:
                 st.info("No HIGH or CRITICAL threats found near your location.")


        # Screenshots section <--- THIS IS THE SCREENSHOT DISPLAY AREA
        st.markdown("<div class='section-header'>SATELLITE IMAGERY</div>", unsafe_allow_html=True)

        # Get screenshots for the selected location
        base_name_full = str(selected_loc_data.get('base_name', '')) # Get full base name (e.g., "Base 1" or "Base_1"), ensure string

        # Attempt to extract number based on expected formats (e.g., "Base_1" or "Base 1")
        base_name_number = '' # Default to empty string

        # Try splitting by underscore first (for "Base_1" format)
        parts_underscore = base_name_full.split('_')
        if parts_underscore and parts_underscore[-1].isdigit():
            base_name_number = parts_underscore[-1]
        else:
            # If underscore split didn't work, try splitting by space (for "Base 1" format)
            parts_space = base_name_full.split()
            if parts_space and parts_space[-1].isdigit():
                 base_name_number = parts_space[-1]

        # The call to the get_screenshots function happens here
        screenshots = get_screenshots(base_name_number, country)


        # Check if screenshots list is empty <-- Display logic starts here
        if not screenshots:
             # If the list is empty, this message is displayed
             st.info("No satellite imagery available for this location.")
        else:
            # If the list is NOT empty, the code enters THIS block to display the images
            # Create tabs for grouping the screenshots (rest of your display code is here)
            if len(screenshots) > 4:
                tab1, tab2 = st.tabs(["Satellite Images 1-4", "Satellite Images 5-8"])

                with tab1:
                    screenshot_cols1 = st.columns(2)
                    for i, screenshot in enumerate(screenshots[:4]):
                        try:
                            with screenshot_cols1[i % 2]:
                                # Ensure screenshot path exists before trying to display
                                if os.path.exists(screenshot):
                                     st.image(screenshot, caption=f"Surveillance Image {i+1}", use_container_width=True)
                                else:
                                     st.warning(f"Screenshot file not found: {screenshot}") # Debug if path is wrong
                        except Exception as e:
                            st.error(f"Error displaying image {screenshot}: {e}")


                with tab2:
                    screenshot_cols2 = st.columns(2)
                    for i, screenshot in enumerate(screenshots[4:8]):
                        try:
                            with screenshot_cols2[i % 2]:
                                # Ensure screenshot path exists before trying to display
                                if os.path.exists(screenshot):
                                     st.image(screenshot, caption=f"Surveillance Image {i+5}", use_container_width=True)
                                else:
                                     st.warning(f"Screenshot file not found: {screenshot}") # Debug if path is wrong
                        except Exception as e:
                            st.error(f"Error displaying image {screenshot}: {e}")

            else:
                # If 4 or fewer screenshots, display in columns without tabs
                screenshot_cols = st.columns(min(len(screenshots), 2))
                for i, screenshot in enumerate(screenshots):
                    try:
                        with screenshot_cols[i % 2]:
                             # Ensure screenshot path exists before trying to display
                             if os.path.exists(screenshot):
                                st.image(screenshot, caption=f"Surveillance Image {i+1}", use_container_width=True)
                             else:
                                st.warning(f"Screenshot file not found: {screenshot}") # Debug if path is wrong
                    except Exception as e:
                        st.error(f"Error displaying image {screenshot}: {e}")
        # ... (Rest of the screenshot display logic ends here) ...

    with col2: # <--- Content for the second column continues
        # Threat assessment
        st.markdown("<div class='section-header'>THREAT ASSESSMENT</div>", unsafe_allow_html=True)

        # Get threat level for selected location
        threat_level = threat_levels.get(selected_loc_key, "UNKNOWN")
        threat_color_class = {
            "CRITICAL": "status-critical",
            "HIGH": "status-critical",
            "MODERATE": "status-warning",
            "LOW": "status-secure",
            "UNKNOWN": ""
        }

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Overall Threat Level</div>
            <div class="key-metric {threat_color_class[threat_level]}">{threat_level}</div>
            <div class="metric-label">Based on intelligence analysis</div>
        </div>
        """, unsafe_allow_html=True)

        # Extract insights
        analyst_history = selected_loc_data.get('analyst_history', [])
        all_findings, all_analyses = extract_insights(analyst_history)

        # Keywords frequency
        keyword_counts = count_keywords(all_findings)

        # Plot keywords
        if keyword_counts:
            # Ensure there's data before trying to unpack and plot
            # Check if the top keyword has a count greater than 0
            if keyword_counts and keyword_counts[0][1] > 0:
                keywords, counts = zip(*keyword_counts[:10])  # Take top 10
                fig = px.bar(
                    x=keywords,
                    y=counts,
                    title="Key Military Features Detected",
                    labels={"x": "Feature", "y": "Frequency"},
                    color=counts,
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(
                    plot_bgcolor="#2a3f5f",
                    paper_bgcolor="#2a3f5f",
                    font_color="#ffffff",
                    margin=dict(l=10, r=10, t=40, b=10),
                    coloraxis_showscale=False,
                     title_font_color="#64ffda" # Title color
                )
                # Update x and y axis label colors
                fig.update_xaxes(title_font_color="#d1d7e0", tickfont_color="#d1d7e0")
                fig.update_yaxes(title_font_color="#d1d7e0", tickfont_color="#d1d7e0")

                st.plotly_chart(fig, use_container_width=True)
            else:
                 st.info("No key military features with significant counts found.")

        else:
            st.info("No keywords to plot.")


        # Activity assessment (using dummy data)
        import random
        activity_level = random.choice(["High", "Moderate", "Low"])
        readiness = random.choice(["Combat Ready", "Operational", "Training", "Maintenance"])
        personnel = random.randint(100, 5000)

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Operational Assessment</div>
            <p><strong>Activity Level:</strong> {activity_level}</p>
            <p><strong>Readiness Status:</strong> {readiness}</p>
            <p><strong>Estimated Personnel:</strong> {personnel}</p>
        </div>
        """, unsafe_allow_html=True)

    # Findings section (Optional)
    if show_findings:
        st.markdown("<div class='section-header'>INTELLIGENCE FINDINGS</div>", unsafe_allow_html=True)

        if all_findings:
            st.markdown("<ul class='findings-list'>", unsafe_allow_html=True)
            for finding in all_findings[:20]:  # Limit to prevent overwhelming
                st.markdown(f"<li>{finding}</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)

            if len(all_findings) > 20:
                st.info(f"{len(all_findings) - 20} more findings available in full report or raw data section.")
        else:
            st.info("No detailed findings available for this location.")

    # Commander's report (Optional)
    if show_commander:
        st.markdown("<div class='section-header'>COMMANDER'S ASSESSMENT</div>", unsafe_allow_html=True)

        commander_report = selected_loc_data.get('commander_report')
        if commander_report:
            # Ensure the commander report is a string before displaying
            if isinstance(commander_report, str):
                 st.markdown(f"""
                 <div class="analyst-report">
                     {commander_report.replace('\n', '<br>')}
                 </div>
                 """, unsafe_allow_html=True)
            else:
                 st.warning("Commander's report data is not in expected format (expected string).")
        else:
            st.info("No commander's report available for this location.")

    # Raw analysis data (Optional)
    if show_raw_data:
        st.markdown("<div class='section-header'>RAW ANALYST REPORTS</div>", unsafe_allow_html=True)
        if analyst_history:
            for i, report in enumerate(analyst_history):
                with st.expander(f"Analyst Report #{i+1}", expanded=False): # Start collapsed
                    try:
                        # Try to parse and display as JSON, fallback to text
                        if isinstance(report, str):
                            report_data = json.loads(report)
                            st.json(report_data)
                        else: # Assume it's already a dict/list
                            st.json(report)
                    except (json.JSONDecodeError, TypeError):
                        st.text(report) # Display as plain text if JSON parsing fails
                    except Exception as e:
                        st.error(f"Error displaying raw report #{i+1}: {e}") # Catch other errors
                        st.text(str(report)) # Display raw content if error occurs
        else:
             st.info("No raw analyst history available for this location.")
    
# Footer
    st.markdown("""
    <div class="footer">
        Military Intelligence Dashboard v1.0 | For authorized personnel only | © 2025 Defense Intelligence Agency
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize session state variables if they don't exist
    # This is crucial for state persistence across script reruns
    if 'selected_location_index' not in st.session_state:
        st.session_state.selected_location_index = 0 # Default to the first location index
    if 'user_lat' not in st.session_state:
         st.session_state.user_lat = 0.0
    if 'user_lon' not in st.session_state:
         st.session_state.user_lon = 0.0
    if 'user_location_name' not in st.session_state:
         st.session_state.user_location_name = ""
    if 'user_geo_lat' not in st.session_state:
         st.session_state.user_geo_lat = None # Use None to indicate no successful geocode yet
    if 'user_geo_lon' not in st.session_state:
         st.session_state.user_geo_lon = None
    if 'location_input_method_radio' not in st.session_state:
        st.session_state.location_input_method_radio = "Coordinates" # Default input method


    main()
    