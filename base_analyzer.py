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
import json
import requests

load_dotenv()

# --- Constants ---
CSV_FILENAME = "military_bases.csv" # Assumes this file exists in the script's directory
ROWS_TO_PROCESS = 1
SCREENSHOT_DIR = "base_screenshots"
GOOGLE_EARTH_WAIT_TIME = 15
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"

# --- Gemini Helper Functions ---
def setup_gemini_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)

def analyze_image_with_gemini(client: genai.Client, image_path: str, country: str, history_of_analysts: list, model_name: str = GEMINI_MODEL) -> Optional[str]:
    try:
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None

        uploaded_file = client.files.upload(file=image_path)
        print("✅ Uploaded image:", uploaded_file)

        extra_context = ""
        if history_of_analysts:
            combined_history = "\n\n--- Previous Analyst Reports ---\n" + "\n\n".join(history_of_analysts)
            extra_context = f"\n\nHere is the analysis of previous analysts about this area and their recommendations. You can use this data but don’t use it as fact, think for yourself: {combined_history}"

        prompt = (
            f"You are an expert in understanding satellite imagery and you work for the US army. "
            f"We got intel that this area is a base/facility of the military of {country}. "
            f"Analyze this image and respond ONLY with a JSON object containing the following keys:\n\n"
            f"1. 'findings': A list of findings that you think are important for the US army to know, including all man-made structures, military equipment, and infrastructure. "
            f"2. 'analysis': A detailed analysis of your findings.\n"
            f"3. 'things_to_continue_analyzing': A list of things that you think are important to continue analyzing in further images.\n"
            f"4. 'action': One of ['zoom-in', 'zoom-out', 'move-left', 'move-right', 'finish'] "
            f"based on what would help you analyze the image or area better."
            f"{extra_context}"
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[uploaded_file, prompt,
        ])

        # Extract text from the response correctly
        raw_text = response.candidates[0].content.parts[0].text.strip("```json\n").strip("```").strip()

        # Try parsing the cleaned JSON
        try:
            parsed_response = json.loads(raw_text)
            print("Parsed Gemini response:", parsed_response)
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            return None

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
def generate_google_earth_url(lat: float, lon: float, altitude: float, distance: float, tilt: float, heading: float) -> str:
    """
    Generates a Google Earth URL for the given latitude and longitude with dynamic parameters
    for zoom level, tilt, and heading.
    """
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

# --- Commander Report Function ---
def generate_commander_report(history: list):
    """
    Generates a final report for the military commander using OpenRouter API.
    """
    print("📡 Generating final commander report using OpenRouter...")

    history_text = "\n\n--- Analyst Report ---\n".join(history)
    prompt = (
        "You are a high-ranking military commander. You have received 8 independent reports from different satellite image analysts. "
        "They have analyzed the same suspected enemy base from different perspectives. Here is what they said:\n\n"
        f"{history_text}\n\n"
        "Your task is to read all the analysis, synthesize key patterns, and produce a final military-grade summary.\n"
        "Include:\n- Key confirmed and likely observations\n- Disagreements or uncertainties\n- Recommendations for further surveillance or action\n"
        "Write your response as a clear report to the US military high command."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        commander_response = response.json()["choices"][0]["message"]["content"]
        print("\n📋 --- COMMANDER FINAL REPORT ---")
        print(commander_response)
        print("---------------------------------\n")
        return commander_response
    except Exception as e:
        print(f"❌ Error generating commander report: {e}")
        return None

# --- Main Processing Function ---
def process_bases(csv_path: str, num_rows: int, screenshot_dir: str, gemini_client: genai.Client):
    """
    Processes the CSV file containing military base coordinates, takes screenshots of Google Earth views
    for each base, and sends the screenshots to Gemini for analysis. This function will loop, repeating actions.
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
        current_zoom = 1000  # initial zoom level
        altitude = current_zoom
        distance = 5000
        tilt = 35
        heading = 0

        for index, row in df.head(num_rows).iterrows():
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                country = row.get('country', 'UnknownCountry')
                base_name_part = row.get('name', f'Base_{index+1}')
                safe_name_part = quote(base_name_part.replace(" ", "_"), safe='')
                print(f"\nProcessing Row {index + 1}: Country={country}, Lat={lat}, Lon={lon}")

                history_of_analysts = []
                loop_count = 0

                while loop_count < 8:
                    loop_count += 1

                    earth_url = generate_google_earth_url(lat, lon, altitude, distance, tilt, heading)
                    print(f"Opening Google Earth: {earth_url}")
                    driver.get(earth_url)

                    screenshot_filename = f"{country}_{safe_name_part}_({lat:.4f},{lon:.4f})_loop{loop_count}.png"
                    screenshot_filepath = os.path.join(screenshot_dir, screenshot_filename)

                    take_screenshot(driver, screenshot_filepath)

                    print("Sending to Gemini for analysis...")
                    response = analyze_image_with_gemini(gemini_client, screenshot_filepath, country, history_of_analysts)

                    if response:
                        response_text = json.dumps(response, indent=2)
                        history_of_analysts.append(response_text)

                        action = response.get("action")
                        if action == "zoom-in":
                            current_zoom -= 500  # Decrease the zoom level to zoom in
                            altitude = current_zoom
                        elif action == "zoom-out":
                            current_zoom += 500  # Increase the zoom level to zoom out
                            altitude = current_zoom
                        elif action == "move-left":
                            heading -= 10  # Move left by changing heading
                        elif action == "move-right":
                            heading += 10  # Move right by changing heading
                        elif action == "finish":
                            print("Analysis complete. No further actions required.")
                            break

                    else:
                        print("⚠️ No response from Gemini.")
                        break

                generate_commander_report(history_of_analysts)

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
