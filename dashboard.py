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
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from urllib.parse import quote

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
    /* --- Overall App Styling (More aggressive root styling) --- */
    /* Target root HTML and Body, ensure no default margin/padding */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #1a2639 !important; /* Ensure body background is dark */
    }

    /* Target the core Streamlit app container view */
    [data-testid="stAppViewContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #1a2639 !important; /* Ensure app container background is dark */
        color: #e6e6e6; /* Set text color for the app */
    }

    /* This targets the main content area container */
    .main {
        background-color: #1a2639 !important; /* Ensure main area background is dark */
        color: #e6e6e6;
        padding: 0 !important; /* Remove default padding */
        margin: 0 !important; /* Remove default margin */
    }

    /* --- FIX: White area at the top when scrolling the main content --- */
    /* Target the inner container that holds the main page content below the header */
    [data-testid="stVerticalBlock"] {
         background-color: #1a2639 !important; /* Ensure this inner block matches background */
         padding: 1rem; /* Example: Add some internal padding */
    }
     /* Also target the block holding the title container */
    [data-testid="stVerticalBlock"] > div:first-child {
         background-color: #1a2639 !important; /* Ensure the very top block matches */
    }
    /* Ensure report containers match background */
     [data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
         background-color: #2a3f5f !important; /* Match expander background for consistency */
     }


    /* --- Sidebar Styling --- */
    [data-testid="stSidebar"] {
        background-color: #1a2639 !important; /* Ensure sidebar background is dark */
        border-right: 1px solid #2a3f5f;
    }
     /* Ensure sidebar content area also has dark background */
    [data-testid="stSidebarContent"] {
         background-color: #1a2639 !important; /* Ensure sidebar content background is dark */
         padding-top: 1rem; /* Add some padding inside sidebar */
    }

    /* --- FIX: Sidebar Arrow Color --- */
    /* Target the button when sidebar is open */
    [data-testid="stSidebarCloseButton"] {
        color: #64ffda !important; /* Change the color of the icon */
        fill: #64ffda !important; /* Ensure SVG fill color is changed */
    }
    /* Target the button when sidebar is closed (the expand arrow) */
    [data-testid="stSidebarExpandButton"] {
        color: #64ffda !important; /* Change the color of the icon */
        fill: #64ffda !important; /* Ensure SVG fill color is changed */
    }
    /* ---------------------------------- */


    /* Sidebar elements */
    .stButton button {
        background-color: #2a3f5f;
        color: #64ffda;
        border: 1px solid #64ffda;
    }
    /* Styling for the selectbox button/display area */
    .stSelectbox > div > div[data-baseweb="select"] {
        background-color: #2a3f5f;
        color: #d1d7e0;
        border: 1px solid #457b9d;
    }

    /* --- Selectbox dropdown list styling --- */
    /* Target the overlay containing the dropdown list */
    div[data-baseweb="popover"] {
        background-color: #2a3f5f !important; /* Background for the popover/dropdown container */
        border: 1px solid #457b9d !important;
        border-radius: 5px; /* Match card/section border-radius */
        overflow: hidden; /* Hide potential default scrollbar styling */
         z-index: 99999 !important; /* Ensure dropdown is above other elements */
    }

    /* Target the list itself within the popover */
     div[data-baseweb="popover"] ul[role="listbox"] {
        background-color: #2a3f5f !important; /* Ensure list background is dark */
        padding: 0 !important; /* Remove default list padding */
     }


    /* Target individual options within the dropdown list */
    div[data-baseweb="popover"] li {
        background-color: #2a3f5f !important; /* Background for options */
        color: #d1d7e0 !important; /* Text color for options */
        padding: 10px 15px !important; /* Adjust padding */
        margin: 0 !important; /* Remove default margins */
    }

    /* Optional: Style for hovered option */
    div[data-baseweb="popover"] li:hover {
         background-color: #457b9d !important; /* Slightly lighter background on hover */
         color:  !important; /* White text on hover */
    }
    /* Optional: Style for selected option (after clicking) */
     div[data-baseweb="popover"] li[aria-selected="true"] {
         background-color: #64ffda !important; /* Highlight color for selected item */
         color: #1a2639 !important; /* Dark text for contrast on highlight */
     }
    /* ------------------------------------------- */


    /* Fix sidebar text visibility */
    .stSelectbox label, .stCheckbox label, .stRadio label, .stNumberInput label, .stTextInput label {
        color: #d1d7e0 !important;
        background-color: transparent !important;
    }

    /* Styling for input fields */
    .stNumberInput input, .stTextInput input {
         background-color: #2a3f5f;
         color: #d1d7e0;
         border: 1px solid #457b9d;
         padding: 0.375rem 0.75rem; /* Adjust padding */
         border-radius: 0.25rem; /* Adjust border-radius */
    }

    /* General container styling */
    .sidebar-menu-item {
        background-color: #2a3f5f;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #64ffda;
    }
    .title-container {
        background-color: #2a3f5f;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1rem; /* Keep margin below header */
        border-left: 5px solid #64ffda;
    }
    .dashboard-title {
        color: #64ffda;
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
        margin: 1rem 0; /* Keep vertical margin around headers */
        border-left: 5px solid #64ffda;
        color: #64ffda;
    }
    .card {
        background-color: #2a3f5f;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem; /* Keep vertical margin below cards */
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
        border-top: 1px solid #2a3f2a; /* Adjusted border color slightly */
        color: #d1d7e0;
    }
    /* Status colors */
    .status-critical { color: #ff5252; font-weight: bold; }
    .status-warning { color: #ffca28; font-weight: bold; }
    .status-secure { color: #4caf50; font-weight: bold; }
    .status-unknown { color: #d1d7e0; font-weight: bold; }

    .findings-list li {
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
     /* Expander styling */
    .st-expander {
        background-color: #2a3f5f !important;
        border-radius: 5px !important;
        border: none !important; /* Remove default border */
    }
    .st-expander > div[data-testid="stVerticalBlock"] {
         background-color: #2a3f5f !important; /* Ensure content inside expander matches */
         padding: 0.75rem 1rem !important; /* Add some padding inside expander content */
    }


     /* Improve text readability with better contrast */
    p, li, div, label, span { /* Added span */
        color: #ffffff; /* Default text color */
    }
     strong {
        color: #ffffff; /* Strong text color */
        font-weight: bold;
    }
    /* Ensure plotly text elements are visible */
    .js-plotly-plot .plotly, .js-plotly-plot .modebar, .js-plotly-plot .gd_settings .gd-sidebar {
        color: #ffffff !important;
        fill: #ffffff !important; /* For SVG text */
    }
     /* Ensure axis labels/ticks are visible in Plotly */
    .js-plotly-plot .xtick, .js-plotly-plot .ytick, .js-plotly-plot .xlabel, .js-plotly-plot .ylabel {
         fill: #d1d7e0 !important; /* Lighter color for axis labels/ticks */
         color: #d1d7e0 !important;
    }
    /* Ensure plot titles/annotations are visible */
    .js-plotly-plot .gtitle, .js-plotly-plot .annotation-text {
         fill: #ffffff !important;
         color: #ffffff !important;
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
        if not os.path.exists("data.json"):
            st.error("data.json file not found. Please ensure the file exists in the current directory.")
            return {}
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure unique keys if they are based on something like name or index
            # For robustness, let's ensure keys are strings if they aren't already
            # And ensure essential fields exist, defaulting to None or empty where appropriate
            processed_data = {}
            for k, v in data.items():
                 processed_data[str(k)] = {
                     'base_name': v.get('base_name', f'Base_{k}'), # Default name if missing
                     'country': v.get('country', 'Unknown Country'),
                     'latitude': v.get('latitude'), # Keep as is, will validate later
                     'longitude': v.get('longitude'), # Keep as is, will validate later
                     'threat_level': v.get('threat_level'), # Keep as is, will validate/default later
                     'analyst_history': v.get('analyst_history', []),
                     'commander_report': v.get('commander_report'),
                     # Add other potential keys with defaults if necessary
                     'estimated_personnel': v.get('estimated_personnel')
                 }
            return processed_data

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
        # Handle cases where analyst_history might be missing or not a list
        # print(f"Warning: analyst_history is not a list: {analyst_history}") # Optional debug
        return [], []


    for report in analyst_history:
        try:
            report_data = None
            if isinstance(report, dict):
                report_data = report
            elif isinstance(report, str):
                 # Attempt to clean potential markdown or extra text
                 clean_report = report.strip()
                 # Remove common JSON markdown fences
                 if clean_report.startswith('```json'):
                     clean_report = clean_report[7:].strip()
                 if clean_report.endswith('```'):
                     clean_report = clean_report[:-3].strip()

                 # Basic check if it looks like JSON before parsing
                 if clean_report.startswith('{') and clean_report.endswith('}') or \
                    clean_report.startswith('[') and clean_report.endswith(']'):
                      report_data = json.loads(clean_report)
                 # else: it's just raw text, we won't extract findings/analysis from it this way


            if report_data: # Proceed only if we got a dict
                if "findings" in report_data and isinstance(report_data["findings"], list):
                    # Ensure all items in findings are strings, convert if necessary
                    all_findings.extend([str(f) for f in report_data["findings"] if f is not None])
                if "analysis" in report_data and isinstance(report_data["analysis"], str):
                    all_analyses.append(report_data["analysis"])

        except (json.JSONDecodeError, TypeError) as e:
            # print(f"Skipping invalid report entry (JSON Error): {report} Error: {e}") # Optional: for debugging
            continue # Skip invalid reports or those that failed parsing
        except Exception as e:
             # Catch any other unexpected errors during processing a report
             print(f"Skipping report due to unexpected error: {report} Error: {e}")
             continue


    return all_findings, all_analyses

# Count frequencies of keywords in findings
def count_keywords(all_findings):
    keywords = {
        "runway": 0, "hangar": 0, "radar": 0, "missile": 0, "vehicle": 0,
        "building": 0, "bunker": 0, "compound": 0, "storage": 0, "facility": 0,
        "aircraft": 0, "defense": 0, "tower": 0, "tank": 0, "base": 0,
        "structure": 0, "equipment": 0, "system": 0, "weapon": 0, "infrastructure": 0,
        "airfield": 0, "port": 0, "ship": 0, "submarine": 0 # Added naval/air terms
    }

    for finding in all_findings:
        if isinstance(finding, str): # Ensure finding is a string
            finding_lower = finding.lower()
            for keyword in keywords:
                # Use regex word boundaries to avoid matching "building" in "rebuilding"
                if re.search(r'\b' + re.escape(keyword) + r'\b', finding_lower):
                    keywords[keyword] += 1

    # Filter out keywords with zero count for cleaner plot
    filtered_keywords = {k: v for k, v in keywords.items() if v > 0}

    # Convert to list of tuples for plotting, sort by count
    sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords

# Get the most recent screenshot for each location
def get_screenshots(base_name):
    screenshot_dir = "base_screenshots"
    screenshots = []

    if not os.path.exists(screenshot_dir):
        # st.warning(f"Screenshot directory not found: {screenshot_dir}") # Optional warning
        return []

    # Create a safe name for file matching - be careful with special characters
    # Using re.escape might be too strict, simple alphanumeric/underscore is safer
    # Let's allow letters, numbers, spaces, underscores, hyphens, and periods
    safe_name_pattern = re.sub(r'[^\w\s.\-]', '', base_name).replace(' ', '_')


    # Regex to match filenames: Country_SafeName_(lat,lon)_loop#.png
    # We need to be flexible with Country and lat/lon as they can vary
    # A pattern that looks for the safe_name_pattern followed by coords and loop number
    # Example: US_Fort_Bliss_(31.8000,-106.4000)_loop5.png
    # Pattern: starts with anything, underscore, safe name, underscore, paren, coords, paren, underscore, loop, digits, dot, png
    # Relaxing the start and end to just contain the core part is safer
    # Use re.escape for the base_name part in case it has regex special chars
    file_pattern = re.compile(rf'.*{re.escape(safe_name_pattern)}_\([\d.-]+,[\d.-]+\)_loop(\d+)\.png$', re.IGNORECASE)


    for filename in os.listdir(screenshot_dir):
        match = file_pattern.match(filename)
        if match:
            try:
                # Extract loop number for sorting
                loop_number = int(match.group(1))
                screenshots.append((os.path.join(screenshot_dir, filename), loop_number))
            except ValueError:
                 # Skip files where loop number is not a valid integer
                 print(f"Warning: Skipping screenshot '{filename}' due to invalid loop number.")
                 continue
            except Exception as e:
                 print(f"Warning: Skipping screenshot '{filename}' due to unexpected error: {e}")
                 continue


    # Sort by loop number descending
    screenshots.sort(key=lambda x: x[1], reverse=True)

    # Return just the file paths, limiting to top N
    return [s[0] for s in screenshots[:4]]


# Assign threat level to each base (using stored or random for demo)
# Modified to use potential 'threat_level' key in data if present
def assign_threat_levels(data):
    import random
    threat_levels = {}

    valid_threats = ["CRITICAL", "HIGH", "MODERATE", "LOW", "UNKNOWN"]

    for loc_key, loc_data in data.items():
        # Use the 'threat_level' key from data.json if it exists and is valid
        stored_threat = loc_data.get('threat_level')
        if stored_threat in valid_threats:
             threat_levels[loc_key] = stored_threat
        else:
            # For demo purposes or if not in data, assign random threat levels
            # Note: In a real app, this would be determined by analysis findings
            threat_level = random.choice(valid_threats[:-1]) # Exclude UNKNOWN from random assignment
            threat_levels[loc_key] = threat_level

    return threat_levels

# Haversine formula to calculate distance between two coordinates
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) in kilometers.
    Returns infinity if coordinates are invalid.
    """
    try:
        # Convert decimal degrees to radians
        lon1_rad, lat1_rad, lon2_rad, lat2_rad = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    except (ValueError, TypeError):
        return float('inf') # Return infinity for invalid inputs
    except Exception as e:
         print(f"Error in haversine calculation: {e}")
         return float('inf')


# Find nearest threat location
def find_nearest_threat(data, threat_levels, current_lat, current_lon):
    nearest_distance = float('inf')
    nearest_base = None
    nearest_threat_level = None
    nearest_base_lat = None
    nearest_base_lon = None

    # Ensure current location is valid numbers and within range
    try:
        current_lat = float(current_lat) if current_lat is not None else None
        current_lon = float(current_lon) if current_lon is not None else None

        if current_lat is None or current_lon is None or \
           not (-90 <= current_lat <= 90 and -180 <= current_lon <= 180):
            # print("Warning: Invalid current location coordinates.") # Optional debug
            return None, None, float('inf'), None, None # Indicate invalid current location
    except (ValueError, TypeError):
         # print("Warning: Invalid current location data type.") # Optional debug
         return None, None, float('inf'), None, None # Indicate invalid current location data type


    for loc_key, loc_data in data.items():
        try:
            base_lat = float(loc_data.get('latitude', 0))
            base_lon = float(loc_data.get('longitude', 0))

            # Skip if base coordinates are invalid or out of range
            if not (-90 <= base_lat <= 90 and -180 <= base_lon <= 180):
                 # print(f"Skipping base '{loc_data.get('base_name')}' due to coordinates out of range.") # Optional debug
                 continue


            distance = haversine(current_lon, current_lat, base_lon, base_lat)

            # Only consider valid distances
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_base = loc_data.get('base_name', 'Unknown Base')
                nearest_threat_level = threat_levels.get(loc_key, "UNKNOWN")
                nearest_base_lat = base_lat
                nearest_base_lon = base_lon

        except (ValueError, TypeError):
             # Skip if coordinates are not valid numbers in the data entry
             # print(f"Warning: Skipping base '{loc_data.get('base_name')}' due to invalid coordinates data type.") # Optional debug
             continue
        except Exception as e:
             # Catch any other unexpected errors during distance calculation for a base
             print(f"Error processing base '{loc_data.get('base_name')}' for nearest threat: {e}")
             continue


    # Return the nearest base name, its threat level, its distance, and its coordinates
    if nearest_base:
         return nearest_base, nearest_threat_level, nearest_distance, nearest_base_lat, nearest_base_lon
    else:
         return None, None, float('inf'), None, None # Indicate no nearest threat found


# Location search using geocoding
def get_location_coordinates(location_name):
    # Use a session-specific geolocator or handle potential timeout/availability issues
    try:
        # Check for empty input
        if not location_name or not location_name.strip():
            st.warning("Please enter a location name or address.")
            return None, None

        geolocator = Nominatim(user_agent="military_intelligence_dashboard_v1.0", timeout=10) # Increased timeout slightly
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
        st.error(f"Location '{location_name}' not found.")
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable):
        st.error("Geocoding service unavailable or timed out. Please try again later.")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred during geocoding: {e}")
        return None, None

# Main function
def main():
    # Load data
    data = load_data()

    if not data:
        # Error message already shown in load_data
        return

    # Assign threat levels
    threat_levels = assign_threat_levels(data)

    # --- Define threat_color dictionary here ---
    # This dictionary is needed in both columns and for the proximity alert,
    # so define it before the column split to ensure it's available.
    threat_color = {
        "CRITICAL": "status-critical",
        "HIGH": "status-critical", # Often High is also considered critical
        "MODERATE": "status-warning",
        "LOW": "status-secure",
        "UNKNOWN": "status-unknown" # Added unknown status color
    }
    # -------------------------------------------


    # Sidebar
    st.sidebar.markdown('<div class="section-header">Intelligence Controls</div>', unsafe_allow_html=True)

    # Create a list of locations for the selectbox
    # Ensure unique keys for the selectbox options if base names aren't unique
    # Using f"{base_name} ({country}) - {threat}" is a good display string,
    # but we need to reliably map back to the original data key.
    # Let's create a mapping from the display string to the original key.
    location_options = []
    location_key_map = {}
    for loc_key, loc_data in data.items():
        # Ensure base_name and country are strings for display
        base_name_display = str(loc_data.get('base_name', 'Unknown Base'))
        country_display = str(loc_data.get('country', 'Unknown Country'))
        threat = threat_levels.get(loc_key, "UNKNOWN")
        display_string = f"{base_name_display} ({country_display}) - {threat}"
        location_options.append(display_string)
        location_key_map[display_string] = loc_key # Map display string back to unique data key

    # Ensure locations are sorted alphabetically by display string for easier finding
    location_options.sort()

    # Handle case where there are no valid locations after loading/processing
    if not location_options:
        st.warning("No valid locations found in data.json to display.")
        return


    # Location selector with improved styling
    selected_location_display = st.sidebar.selectbox(
        "Select Target Location",
        options=location_options,
        index=0 # Default to the first location in the sorted list
    )

    # Get the data for the selected location using the key map
    selected_loc_key = location_key_map.get(selected_location_display)

    # This check should ideally not fail if location_options came from data.keys()
    # but keeping defensive programming is good.
    if selected_loc_key is None or selected_loc_key not in data:
        st.error("Internal Error: Selected location data could not be retrieved.")
        return # Exit if we can't find the data

    selected_loc_data = data[selected_loc_key]

    # Sidebar - additional filters and controls with improved styling
    st.sidebar.markdown('<div class="sidebar-menu-item">Analysis Filters</div>', unsafe_allow_html=True)
    show_findings = st.sidebar.checkbox("Show Detailed Findings", value=True)
    show_commander = st.sidebar.checkbox("Show Commander's Report", value=True)
    show_raw_data = st.sidebar.checkbox("Show Raw Analysis Data", value=False)

    # Map display options - removed heatmap option
    st.sidebar.markdown('<div class="sidebar-menu-item">Map Display Options</div>', unsafe_allow_html=True)
    show_all_bases = st.sidebar.checkbox("Show All Bases on Map", value=True)

    # Add a section for your location
    st.sidebar.markdown('<div class="sidebar-menu-item">Your Location</div>', unsafe_allow_html=True)
    location_input_method = st.sidebar.radio(
        "Set Your Location By:",
        ("Coordinates", "Address/Location Name"),
        key='location_input_method' # Added key for reliability
    )

    # Use session state to store user location coordinates persistently
    if 'current_lat' not in st.session_state:
        st.session_state.current_lat = None
    if 'current_lon' not in st.session_state:
        st.session_state.current_lon = None
    if 'location_search_term' not in st.session_state:
         st.session_state.location_search_term = ""


    if location_input_method == "Coordinates":
        st.session_state.current_lat = st.sidebar.number_input(
            "Your Latitude",
            value=st.session_state.current_lat if st.session_state.current_lat is not None else 0.0,
            format="%.6f",
            key='user_lat_input',
             help="Enter your current latitude in decimal degrees." # Added help text
        )
        st.session_state.current_lon = st.sidebar.number_input(
            "Your Longitude",
            value=st.session_state.current_lon if st.session_state.current_lon is not None else 0.0,
            format="%.6f",
            key='user_lon_input',
             help="Enter your current longitude in decimal degrees." # Added help text
        )
         # Optional: Add a button to clear location
        if st.sidebar.button("Clear My Location", key='clear_coord_loc'):
            st.session_state.current_lat = None
            st.session_state.current_lon = None
            st.session_state.location_search_term = "" # Also clear search term if present
            st.rerun() # Rerun to clear location display


    else: # Address/Location Name
        st.session_state.location_search_term = st.sidebar.text_input(
            "Enter Address or Location Name",
            value=st.session_state.location_search_term,
            key='location_name_input',
             help="Enter a city, address, or landmark to find your location." # Added help text
        )
        if st.sidebar.button("Search Location", key='search_loc_button'):
            if st.session_state.location_search_term:
                # Geocoding function handles errors and st.error messages
                lat, lon = get_location_coordinates(st.session_state.location_search_term)
                if lat is not None and lon is not None:
                    st.session_state.current_lat = lat
                    st.session_state.current_lon = lon
                    st.sidebar.success(f"Location found at: {lat:.6f}, {lon:.6f}")
                    st.rerun() # Rerun to update map and proximity
                # else: error message is handled by get_location_coordinates

        # Optional: Add a button to clear location
        if st.sidebar.button("Clear My Location", key='clear_search_loc'):
            st.session_state.current_lat = None
            st.session_state.current_lon = None
            st.session_state.location_search_term = ""
            st.rerun() # Rerun to clear location display


    # Get the current user location from session state
    current_lat = st.session_state.current_lat
    current_lon = st.session_state.current_lon


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

    with col1:
        # Target Information
        # Add check if base_name exists before calling .upper()
        base_name_display = selected_loc_data.get('base_name', 'Unknown Base')
        st.markdown(f"<div class='section-header'>TARGET: {base_name_display.upper()}</div>", unsafe_allow_html=True)

        loc_cols = st.columns(3)
        with loc_cols[0]:
            st.markdown(f"**Country:** {selected_loc_data.get('country', 'N/A')}")
        with loc_cols[1]:
            # Format coordinates, show N/A if None
            lat_val = selected_loc_data.get('latitude')
            lon_val = selected_loc_data.get('longitude')
            lat_display = f"{lat_val:.6f}" if lat_val is not None else 'N/A'
            lon_display = f"{lon_val:.6f}" if lon_val is not None else 'N/A'
            st.markdown(f"**Latitude:** {lat_display}")
        with loc_cols[2]:
             st.markdown(f"**Longitude:** {lon_display}")


        # Map
        st.markdown("<div class='section-header'>GEOSPATIAL POSITIONING</div>", unsafe_allow_html=True)

        # Ensure we have valid numerical coordinates for the selected base for centering
        selected_lat_for_map = 0.0
        selected_lon_for_map = 0.0
        valid_selected_coords = False

        try:
            selected_lat = float(selected_loc_data.get('latitude', 0))
            selected_lon = float(selected_loc_data.get('longitude', 0))

             # Check if coordinates are within valid range
            if (-90 <= selected_lat <= 90 and -180 <= selected_lon <= 180):
                 selected_lat_for_map = selected_lat
                 selected_lon_for_map = selected_lon
                 valid_selected_coords = True
            else:
                 st.warning(f"Invalid coordinates found for {base_name_display}. Cannot center map precisely.")

        except (ValueError, TypeError):
            st.warning(f"Invalid coordinates data type for {base_name_display}. Cannot center map precisely.")


        # Create map - start with zoom level based on selection and valid coords
        # If selected coords are invalid, default to a global view
        initial_map_location = [selected_lat_for_map, selected_lon_for_map] if valid_selected_coords else [20, 0] # Center near equator if invalid or 0,0
        initial_zoom = 14 if (valid_selected_coords and not show_all_bases) else 2 # Zoom in if valid & not showing all, otherwise global view


        m = folium.Map(location=initial_map_location,
                      zoom_start=initial_zoom,
                      tiles="CartoDB dark_matter")

        # Add markers for all bases if requested
        if show_all_bases:
            for loc_key, loc_data in data.items():
                try:
                    # Ensure we have valid numerical coordinates for each base marker
                    lat = float(loc_data.get('latitude', 0))
                    lon = float(loc_data.get('longitude', 0))

                    # Skip if coordinates are invalid or out of range
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                         # print(f"Skipping marker for {loc_data.get('base_name')}: Coordinates out of range ({lat}, {lon})") # Optional debug
                         continue


                    base_name = str(loc_data.get('base_name', 'Unknown Base'))
                    country = str(loc_data.get('country', 'Unknown Country'))
                    threat = str(threat_levels.get(loc_key, "UNKNOWN"))

                    # Determine marker color based on threat level using the defined dictionary
                    # Use .get() with a default for safety, remove 'status-' prefix for icon color string
                    icon_color = threat_color.get(threat, 'status-unknown').replace('status-', '')
                    if icon_color == 'unknown': icon_color = 'blue' # Folium default for unknown

                    # Add marker
                    popup_html = f"""
                    <div style="font-family: Arial; width: 200px;">
                        <h4>{base_name}</h4>
                        <b>Country:</b> {country}<br>
                        <b>Threat Level:</b> {threat}<br>
                        <b>Coordinates:</b> {lat:.4f}, {lon:.4f}
                    </div>
                    """

                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{base_name} ({threat})",
                        icon=folium.Icon(color=icon_color, icon="crosshairs", prefix="fa")
                    ).add_to(m)
                except (ValueError, TypeError) as e:
                    # Skip this marker if there's an error with coordinates type
                    # print(f"Skipping marker for {loc_data.get('base_name')}: Invalid coordinates data type {e}") # Optional debug
                    continue
                except Exception as e:
                     # Catch any other unexpected errors during marker creation
                     print(f"Skipping marker for {loc_data.get('base_name')}: Unexpected error {e}")
                     continue

        else:
            # Just add the selected base marker if its coordinates are valid
             if valid_selected_coords:
                icon_color = threat_color.get(threat_levels.get(selected_loc_key, 'UNKNOWN'), 'status-unknown').replace('status-', '')
                if icon_color == 'unknown': icon_color = 'blue' # Folium default for unknown

                folium.Marker(
                    [selected_lat_for_map, selected_lon_for_map],
                    popup=selected_loc_data.get('base_name', 'Unknown Base'),
                    tooltip=selected_loc_data.get('base_name', 'Unknown Base'),
                    # Use threat color for single base marker too
                    icon=folium.Icon(color=icon_color, icon="crosshairs", prefix="fa")
                ).add_to(m)


        # Add user's location marker if coordinates are provided and valid
        # Check if current_lat/lon are not None and within a plausible range
        if current_lat is not None and current_lon is not None and \
           (-90 <= current_lat <= 90 and -180 <= current_lon <= 180):

            # Add user location marker
            folium.Marker(
                [current_lat, current_lon],
                popup="Your Location",
                tooltip="Your Location",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)

            # Find nearest threat (includes lat/lon return now)
            # This finds the geographically nearest base regardless of its threat level
            nearest_base, nearest_threat, nearest_distance, threat_lat, threat_lon = find_nearest_threat(
                data, threat_levels, current_lat, current_lon)

            if nearest_base and threat_lat is not None and threat_lon is not None and nearest_distance != float('inf'):
                # Add a line connecting your location to the nearest threat
                folium.PolyLine(
                    locations=[[current_lat, current_lon], [threat_lat, threat_lon]],
                    color="#64ffda",
                    weight=2,
                    opacity=0.7,
                    dash_array="5"
                ).add_to(m)

                # Add info on the map about distance
                # Position the label near the midpoint, slightly offset
                mid_lat = (current_lat + threat_lat) / 2
                mid_lon = (current_lon + threat_lon) / 2

                folium.Marker(
                    [mid_lat, mid_lon],
                    popup=f"Distance: {nearest_distance:.1f} km",
                    tooltip=f"{nearest_distance:.1f} km",
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                            position: relative; top: -20px; left: -30px; /* Adjust offset as needed */
                            color: white;
                            background-color: rgba(42, 63, 95, 0.9); /* Slightly more opaque */
                            padding: 5px;
                            border: 1px solid #64ffda;
                            border-radius: 5px;
                            font-size: 10px;
                            font-weight: bold;
                            white-space: nowrap; /* Prevent text wrapping */
                            z-index: 1000; /* Ensure it's above lines */
                        ">{nearest_distance:.1f} km</div>
                        """
                    )
                ).add_to(m)

            # else: # Optional: Add a message if user location is valid but no bases found in data
            #      if nearest_distance == float('inf'):
            #           st.info("No military bases found in the dataset to calculate nearest threat from your location.")


        # Add circle around selected base if coordinates are valid
        if valid_selected_coords:
            folium.Circle(
                radius=2000, # 2km radius
                location=[selected_lat_for_map, selected_lon_for_map],
                color="#64ffda",
                fill=True,
                fill_opacity=0.2,
                tooltip=f"Approx. 2km radius around {base_name_display}"
            ).add_to(m)

        # Display map
        folium_static(m, width=650, height=400)

        # Display nearest threat info below the map if user location is provided and a nearest base was found
        if current_lat is not None and current_lon is not None and \
           (-90 <= current_lat <= 90 and -180 <= current_lon <= 180):

             # Re-find nearest threat to get the details shown below the map
             # This avoids re-running the function unnecessarily if already done for the map line
            nearest_base, nearest_threat, nearest_distance, _, _ = find_nearest_threat(
                data, threat_levels, current_lat, current_lon)

            if nearest_base and nearest_distance != float('inf'):
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Proximity Alert</div>
                    <p><strong>Nearest Threat:</strong> {nearest_base}</p>
                    <p><strong>Threat Level:</strong> <span class="{threat_color.get(nearest_threat, 'status-unknown')}">{nearest_threat}</span></p>
                    <p><strong>Distance:</strong> {nearest_distance:.1f} km</p>
                </div>
                """, unsafe_allow_html=True)
            elif not nearest_base and current_lat is not None: # Only show this if location is set but no base found
                 st.info("No military bases found in the dataset to calculate nearest threat from your location.")


        # Screenshots section
        st.markdown("<div class='section-header'>SATELLITE IMAGERY</div>", unsafe_allow_html=True)

        # Get screenshots for the selected location
        screenshots = get_screenshots(selected_loc_data.get('base_name', '')) # Pass base name

        if screenshots:
            # Determine number of columns based on number of screenshots (max 2)
            num_screenshot_cols = min(len(screenshots), 2)
            # Ensure at least one column if there are screenshots
            if num_screenshot_cols == 0 and len(screenshots) > 0: num_screenshot_cols = 1
            if num_screenshot_cols > 0: # Only create columns if there are screenshots to display
                 screenshot_cols = st.columns(num_screenshot_cols)

                 for i, screenshot in enumerate(screenshots[:4]): # Limit to max 4 images
                     try:
                         # Use modulo to cycle through the columns
                         with screenshot_cols[i % num_screenshot_cols]:
                             st.image(screenshot, caption=f"Surveillance Image {i+1}", use_container_width=True)
                     except Exception as e:
                         st.error(f"Error loading image {screenshot}: {e}")
            else:
                 st.info("No satellite imagery available for this location.")
        else:
            st.info("No satellite imagery available for this location.")


    with col2:
        # Threat assessment
        st.markdown("<div class='section-header'>THREAT ASSESSMENT</div>", unsafe_allow_html=True)

        # Get threat level for selected location
        threat_level = threat_levels.get(selected_loc_key, "UNKNOWN")

        # Use the threat_color dictionary already defined before columns

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Overall Threat Level</div>
            <div class="key-metric {threat_color.get(threat_level, 'status-unknown')}">{threat_level}</div>
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
            keywords, counts = zip(*keyword_counts[:8])  # Take top 8 most frequent
            fig = px.bar(
                x=keywords,
                y=counts,
                title="Key Military Features Detected",
                labels={"x": "Feature", "y": "Frequency"},
                color=counts,
                color_continuous_scale="Viridis" # Or "Plasma", "Inferno", etc.
            )
            fig.update_layout(
                plot_bgcolor="#2a3f5f",
                paper_bgcolor="#2a3f5f",
                font_color="#ffffff",
                margin=dict(l=10, r=10, t=40, b=10),
                coloraxis_showscale=False,
                 xaxis_title="Feature", # Ensure titles are explicit
                 yaxis_title="Frequency"
            )
             # Improve title font color if default isn't caught by font_color
            fig.update_layout(title_font_color="#ffffff") # Explicitly set title color


            st.plotly_chart(fig, use_container_width=True)
        else:
             st.info("No key features detected from analysis.")

        # Activity assessment (using random values as in original code or data)
        # In a real scenario, this would come from analysis or other intel
        import random
        # Check if activity_level/readiness/personnel are in data, otherwise use random/default
        activity_level = selected_loc_data.get('activity_level', random.choice(["High", "Moderate", "Low", "Unknown"]))
        readiness = selected_loc_data.get('readiness_status', random.choice(["Combat Ready", "Operational", "Training", "Maintenance", "Unknown"]))
        personnel = selected_loc_data.get('estimated_personnel')
        if personnel is None: # If not in data, generate based on activity or default
             personnel = random.randint(100, 5000) if activity_level != "Unknown" and isinstance(activity_level, str) else "N/A"
        else:
             personnel = str(personnel) # Ensure it's a string for display

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Operational Assessment</div>
            <p><strong>Activity Level:</strong> {activity_level}</p>
            <p><strong>Readiness Status:</strong> {readiness}</p>
            <p><strong>Estimated Personnel:</strong> {personnel}</p>
        </div>
        """, unsafe_allow_html=True)

    # Findings section
    if show_findings:
        st.markdown("<div class='section-header'>INTELLIGENCE FINDINGS</div>", unsafe_allow_html=True)

        if all_findings:
            # Use an expander if there are many findings
            if len(all_findings) > 15:
                 with st.expander(f"View All {len(all_findings)} Findings"):
                     st.markdown("<ul class='findings-list'>", unsafe_allow_html=True)
                     for finding in all_findings:
                         st.markdown(f"<li>{finding}</li>", unsafe_allow_html=True)
                     st.markdown("</ul>", unsafe_allow_html=True)
            else:
                 st.markdown("<ul class='findings-list'>", unsafe_allow_html=True)
                 for finding in all_findings:
                     st.markdown(f"<li>{finding}</li>", unsafe_allow_html=True)
                 st.markdown("</ul>", unsafe_allow_html=True)

        else:
            st.info("No detailed findings available for this location.")

    # Commander's report - Now with matching background color
    if show_commander:
        st.markdown("<div class='section-header'>COMMANDER'S ASSESSMENT</div>", unsafe_allow_html=True)

        # Prefer 'analysis' from the last report if commander_report is not in data
        commander_report = selected_loc_data.get('commander_report')
        if not commander_report and all_analyses:
             # Use the analysis from the most recent *valid* report
             # Ensure all_analyses contains strings
             valid_analyses_strings = [a for a in all_analyses if isinstance(a, str) and a.strip()]
             if valid_analyses_strings:
                commander_report = valid_analyses_strings[-1]
             else:
                 commander_report = None # No valid analysis found

        if commander_report and isinstance(commander_report, str): # Ensure it's a non-empty string
            st.markdown(f"""
            <div class="analyst-report">
                {commander_report.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No commander's assessment available for this location.")

    # Raw analysis data
    if show_raw_data:
        st.markdown("<div class='section-header'>RAW ANALYST REPORTS</div>", unsafe_allow_html=True)

        if analyst_history:
            for i, report in enumerate(analyst_history):
                with st.expander(f"Analyst Report #{i+1}"):
                    try:
                        if isinstance(report, str):
                             # Attempt to clean potential markdown before loading as JSON
                             clean_report = report.strip()
                             if clean_report.startswith('```json'):
                                 clean_report = clean_report[7:].strip()
                             if clean_report.endswith('```'):
                                 clean_report = clean_report[:-3].strip()

                             # Attempt JSON parse
                             report_data = json.loads(clean_report)
                             st.json(report_data)
                        elif isinstance(report, dict):
                            st.json(report)
                        else:
                            st.text(f"Non-JSON/Dict data: {report}") # Display if not string/dict
                    except json.JSONDecodeError:
                        st.text(f"Raw Text (JSON Parse Error): {report}") # Show raw text if JSON parsing fails
                    except Exception as e:
                        st.text(f"Raw Text (Unexpected Error: {e}): {report}")

        else:
             st.info("No raw analyst reports available for this location.")


    # Footer
    st.markdown("""
    <div class="footer">
        Military Intelligence Dashboard v1.0 | For authorized personnel only | © 2025 Defense Intelligence Agency
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()