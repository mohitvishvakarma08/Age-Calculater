# Age Calculator

A Flask web application for calculating exact age between two dates. It supports `dd/mm/yyyy` input, calendar selection, validation, recent browser history, and exports to PDF, Excel, Word, and text table formats.

## Features

- Calculates years, months, and days.
- Shows total months, weeks, days, hours, and minutes.
- Calculates weekday, next birthday, and next birthday date.
- Predicts an age group with a trained 1-nearest-neighbor AIML classifier.
- Accepts typed dates with automatic `/` formatting.
- Validates impossible dates such as `31/02/2001`.
- Stores the latest 10 calculations in browser `localStorage`.
- Clicking a history entry restores its complete result.
- Exports reports as PDF, XLSX, DOCX, or TXT.
- Uses the entered name for the export filename, for example `Ankit's age.pdf`.

## Requirements

- Python 3.10 or newer
- Packages listed in `requirements.txt`

## Technologies and tools

- Python and Flask for the server and API
- HTML, CSS, and JavaScript for the browser interface
- `datetime` and `calendar` for date calculations
- A dependency-free 1-nearest-neighbor classifier for age-group prediction
- ReportLab, openpyxl, and python-docx for exports
- Python `unittest` for automated tests
- Git and Render/Gunicorn for version control and deployment

## Local setup

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Tests

Run the automated test suite with:

```bash
python -m unittest discover -s tests -v
```

The tests cover successful calculations, age-group predictions, invalid requests, date ordering, leap-day birthdays, export tables, filenames, and unsupported formats.

## Screenshots

Screenshots of the interface, validation, history, calculation result, and PDF/Excel/Word/text exports are available in the `screenshots/` folder and embedded in `project_report.md`.

## Project structure

```text
app.py                  Flask routes and age calculation logic
requirements.txt        Python dependencies
render.yaml             Render deployment configuration
static/app.js           Form behavior, history, validation, and downloads
static/style.css        Responsive interface styling
templates/index.html    Main page markup
tests/test_app.py       Automated application tests
statement.md            Project statement
uml.md                  UML diagrams
architecture.md         System architecture diagram and notes
workflow.md             User workflow diagram
project_report.md       Project report
```

## Deployment

The included `render.yaml` installs `requirements.txt` and starts the application with Gunicorn:

```bash
gunicorn app:app
```

## Data and privacy

Calculation history is stored only in the current browser's local storage. It is not sent to the Flask server unless the user submits a calculation or exports a result.
