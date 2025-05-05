import os
import time
import pandas as pd
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from google import genai
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- Constants ---
CSV_FILENAME = "military_bases.csv" # Assumes this file exists in the script's directory
ROWS_TO_PROCESS = 1
SCREENSHOT_DIR = "base_screenshots"
GOOGLE_EARTH_WAIT_TIME = 15
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# --- Gemini Helper Functions ---
def setup_gemini_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)

def analyze_image_with_gemini(client: genai.Client, image_path: str, country: str, model_name: str = GEMINI_MODEL) -> Optional[str]:
    try:
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None

        uploaded_file = client.files.upload(file=image_path)
        prompt = (
            f"You are an expert in understanding satellite imagery and you work for the US army. "
            f"We got intel that this area is a base/facility of the military of {country}. "
            f"Analyze this image and respond ONLY with a JSON object containing the following keys:\n\n"
            f"1. 'findings': A list of findings that you think are important for the US army to know, including all man-made structures, military equipment, and infrastructure. "
            f"We are trying to find which systems, weapons, or equipment are present so focus on that.\n"
            f"2. 'analysis': A detailed analysis of your findings.\n"
            f"3. 'things_to_continue_analyzing': A list of things that you think are important to continue analyzing in further images.\n"
            f"4. 'action': One of ['zoom-in', 'zoom-out', 'move-left', 'move-right', 'finish'] "
            f"based on what would help you analyze the image or area better."
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[uploaded_file, prompt],
        )
        return response.text
    except Exception as e:
        print(f"❌ Error during Gemini analysis: {e}")
        return None

# --- WebDriver Setup ---
def setup_driver() -> webdriver.Chrome:
    """Sets up the Selenium Chrome WebDriver."""
    print("Setting up Chrome WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--use-gl=desktop")
    chrome_options.add_argument("--enable-unsafe-webgpu")
    chrome_options.add_argument("--ignore-gpu-blocklist")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# --- Google Earth URL Generator ---
def generate_google_earth_url(lat: float, lon: float) -> str:
    """
    Generates a Google Earth URL for the given latitude and longitude.
    Includes parameters for a reasonable starting view (altitude, distance, tilt).
    """
    altitude = 1000  # meters (approx)
    distance = 5000  # meters
    tilt = 35        # degrees
    heading = 0      # North
    return f"https://earth.google.com/web/@{lat:.6f},{lon:.6f},{altitude}a,{distance}d,{tilt}y,{heading}h"

# --- Screenshot Logic ---
def take_screenshot(driver: webdriver.Chrome, filepath: str):
    """
    Takes a screenshot of the current Google Earth view and saves it to the specified filepath.
    """
    print(f"Waiting {GOOGLE_EARTH_WAIT_TIME} seconds for Google Earth to load...")
    time.sleep(GOOGLE_EARTH_WAIT_TIME)
    print(f"Taking screenshot: {filepath}")
    driver.save_screenshot(filepath)
    print("Screenshot saved.")

# --- Main Processing Function ---
def process_bases(csv_path: str, num_rows: int, screenshot_dir: str, gemini_client: genai.Client):
    """
    Processes the CSV file containing military base coordinates, takes screenshots of Google Earth views
    for each base, and sends the screenshots to Gemini for analysis.
    """
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        print("CSV must contain 'latitude' and 'longitude' columns.")
        return

    os.makedirs(screenshot_dir, exist_ok=True)
    driver = setup_driver()

    try:
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

                print("Sending to Gemini for analysis...")
                response = analyze_image_with_gemini(gemini_client, screenshot_filepath, country)
                if response:
                    print("\n--- GEMINI ANALYSIS ---")
                    print(response)
                    print("------------------------\n")
                else:
                    print("⚠️ No response from Gemini.")

            except ValueError as ve:
                print(f"Invalid coordinates on row {index+1}: {ve}")
            except Exception as e:
                print(f"Error processing row {index+1}: {e}")

    finally:
        print("Closing WebDriver.")
        driver.quit()

# --- Main ---
if __name__ == "__main__":
    print("Starting military base analyzer...")
    gemini_client = setup_gemini_client(GEMINI_API_KEY)
    process_bases(CSV_FILENAME, ROWS_TO_PROCESS, SCREENSHOT_DIR, gemini_client)
