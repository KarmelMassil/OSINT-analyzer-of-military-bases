import os
import time
# import requests # No longer needed for downloading
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote # To handle potential special characters in names

# --- Constants ---
# CSV_URL = "..." # No longer needed
CSV_FILENAME = "military_bases.csv" # Assumes this file exists in the script's directory
ROWS_TO_PROCESS = 5
SCREENSHOT_DIR = "base_screenshots"
GOOGLE_EARTH_WAIT_TIME = 15 # Seconds to wait for Google Earth to load

# --- Functions ---

# download_csv function removed as it's no longer needed

def setup_driver() -> webdriver.Chrome:
    """Sets up the Selenium Chrome WebDriver."""
    print("Setting up Chrome WebDriver...")
    chrome_options = Options()
    # Headless mode is OFF by default
    # chrome_options.add_argument("--headless") # Keep commented out for debugging
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("WebDriver setup complete.")
    return driver

def generate_google_earth_url(lat: float, lon: float) -> str:
    """
    Generates a Google Earth URL for the given latitude and longitude.
    Includes parameters for a reasonable starting view (altitude, distance, tilt).
    """
    altitude = 1000  # meters (approx)
    distance = 5000  # meters
    tilt = 35        # degrees
    heading = 0      # degrees (0=North)

    url = f"https://earth.google.com/web/@{lat:.6f},{lon:.6f},{altitude}a,{distance}d,{tilt}y,{heading}h"
    return url

def take_screenshot(driver: webdriver.Chrome, filepath: str):
    """Takes a screenshot and saves it to the specified path after waiting."""
    try:
        print(f"Waiting {GOOGLE_EARTH_WAIT_TIME} seconds for Google Earth to load...")
        time.sleep(GOOGLE_EARTH_WAIT_TIME)
        print(f"Taking screenshot: {filepath}")
        driver.save_screenshot(filepath)
        print("Screenshot saved.")
    except Exception as e:
        print(f"Error taking screenshot for {filepath}: {e}")

def process_bases(csv_path: str, num_rows: int, screenshot_dir: str):
    """Reads the CSV, opens Google Earth for each base, and takes screenshots."""
    # Check if the pre-downloaded CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at '{csv_path}'.")
        print("Please make sure 'military_bases.csv' is in the same directory as the script.")
        return

    print(f"Processing the first {num_rows} rows from '{csv_path}'...")
    driver = None
    try:
        df = pd.read_csv(csv_path)

        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            print("Error: CSV must contain 'latitude' and 'longitude' columns.")
            return

        driver = setup_driver()
        os.makedirs(screenshot_dir, exist_ok=True)
        print(f"Screenshots will be saved in '{screenshot_dir}'")

        for index, row in df.head(num_rows).iterrows():
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                country = row.get('country', 'UnknownCountry')
                base_name_part = row.get('name', f'Base_{index+1}')
                safe_name_part = quote(base_name_part.replace(" ", "_"), safe='')


                print(f"\nProcessing Row {index + 1}: Country={country}, Lat={lat}, Lon={lon}")

                earth_url = generate_google_earth_url(lat, lon)
                print(f"Opening Google Earth: {earth_url}")
                driver.get(earth_url)

                screenshot_filename = f"{country}_{safe_name_part}_({lat:.4f},{lon:.4f}).png"
                screenshot_filepath = os.path.join(screenshot_dir, screenshot_filename)

                take_screenshot(driver, screenshot_filepath)

            except ValueError as ve:
                print(f"Skipping row {index + 1} due to invalid latitude/longitude: {ve}")
                continue
            except Exception as e:
                print(f"An error occurred processing row {index + 1}: {e}")

    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file '{csv_path}' is empty.")
    except FileNotFoundError: # Should be caught by the initial check, but good practice
        print(f"Error: Could not find the CSV file '{csv_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
    finally:
        if driver:
            print("\nClosing WebDriver.")
            driver.quit()
        print("Processing finished.")

# --- Main Execution ---
if __name__ == "__main__":
    # Directly process the bases, assuming the CSV file exists locally
    print(f"Script started. Assuming '{CSV_FILENAME}' exists locally.")
    process_bases(CSV_FILENAME, ROWS_TO_PROCESS, SCREENSHOT_DIR)