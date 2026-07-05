# OSINT Analyzer of Military Bases

This project is an automated Open-Source Intelligence (OSINT) tool designed to investigate and analyze satellite imagery of global military bases using a multi-agent AI workflow. It fulfills the requirements for Exercise 2 in the "Idea to reality using AI" assignment.

## Features

* **Automated Satellite Reconnaissance:** Uses Selenium to autonomously navigate Google Earth, locate military bases via GPS coordinates provided in `military_bases.csv`, and capture screenshots of the facilities.
* **Multi-Agent AI Analysis:**
    * **The Analyst:** Powered by Google AI Studio's vision-capable models. It examines screenshots to identify military equipment, man-made structures, and infrastructure, outputting structured JSON reports detailing its findings and suggesting further navigation actions (e.g., zoom-in, move-left).
    * **The Commander:** Powered by an OpenRouter reasoning model. It synthesizes historical data and multiple analyst reports to generate a comprehensive, strategic final intelligence brief.
* **Interactive Dashboard:** Includes a `dashboard.py` application to visualize the geographic distribution of the analyzed bases and dynamically display the generated AI intelligence reports.

## Files Included

* `.gitignore`
* `README.md`
* `base_analyzer.py`
* `dashboard.py`
* `military_bases.csv`

## Prerequisites

* Python 3.8+
* Google Chrome and ChromeDriver
* Google AI Studio API Key
* OpenRouter API Key

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install selenium requests pandas google-genai streamlit folium
```

## Configuration

Set up your API keys as environment variables before running the scripts.

For Linux/macOS:
```bash
export GEMINI_API_KEY="your_google_ai_studio_key"
export OPENROUTER_API_KEY="your_openrouter_key"
```

For Windows:
```cmd
set GEMINI_API_KEY="your_google_ai_studio_key"
set OPENROUTER_API_KEY="your_openrouter_key"
```

## Usage

To initiate the automated reconnaissance and analysis workflow:

```bash
python base_analyzer.py
```

To launch the interactive results dashboard:

```bash
streamlit run dashboard.py
```