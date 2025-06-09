# CAN Log Analyzer

A web-based tool for analyzing CAN log files using Streamlit, Plotly, and cantools.

---

## Features

- Upload and parse CAN log files (`.asc`, `.blf`)
- Load CAN database files (`.dbc`)
- Visualize and plot selected CAN signals interactively
- User-friendly web interface with sidebar controls
- Interactive signal selection and customizable plots (scatter, line, heatmap)
- Grid and axis customization for detailed analysis

---

## Environment Setup (Windows)

You can set up the environment in several ways:

### 1. Using Git

Clone the repository and set up a virtual environment:

```powershell
git clone https://github.com/chaitu-ycr/can_log_analyzer.git
cd can_log_analyzer
scripts/venv_setup.bat
.venv/Scripts/Activate
```

### 2. Using pip

Install directly from the repository:

```powershell
pip install git+https://github.com/chaitu-ycr/can_log_analyzer.git
```

### 3. Using uv

Add the package using [uv](https://github.com/astral-sh/uv):

```powershell
uv add https://github.com/chaitu-ycr/can_log_analyzer.git
```

---

## Running the CAN Log Analyzer Web App

To start the web application, run:

```powershell
python -m can_log_analyzer.run_web_app
```

- The app will launch in your default web browser at `http://localhost:8501` (unless otherwise configured).
- Use the sidebar to upload your CAN log files (`.asc`, `.blf`) and CAN database files (`.dbc`).
- Select channels, messages, and signals to visualize.
- Choose plot type and customize grid/axis options as needed.
- Interactive plots and analysis will be available after loading your files.

---

## Notes

- Ensure you are using Python 3.9–3.13 as specified in the project requirements.
- Only `.dbc` files are supported for CAN database input.