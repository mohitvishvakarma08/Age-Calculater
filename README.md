# Age Calculator Project

A Flask-based web application that calculates a person's exact age between two dates and exports the result as a professional report. The project includes browser-side validation, recent calculation history, age-group prediction, and downloadable files in PDF, Excel, Word, and text formats.

## Project overview

This application helps users:
- calculate age with years, months, and days
- compare a date of birth with a selected reference date
- view totals such as months, weeks, days, hours, and minutes
- predict the age group using a simple nearest-neighbor logic model
- restore recent results from browser history
- export the result as a report file in multiple formats

## Key features

- Date validation for invalid or reversed inputs
- Automatic date formatting support for typed values
- Local browser history for the latest 10 results
- Age-group prediction logic built into the app
- Export to PDF, XLSX, DOCX, and TXT
- File naming based on the user-provided name
- Responsive web interface

## Technology stack

- Python 3.10+
- Flask
- HTML, CSS, JavaScript
- ReportLab for PDF generation
- openpyxl for Excel export
- python-docx for Word export
- unittest for automated validation

## Project structure

```text
app.py                        Flask application and export logic
requirements.txt              Dependency list
render.yaml                   Render deployment config
static/app.js                 UI logic, validation, history, and export handling
static/style.css              Styling for the web interface
templates/index.html          Page layout and forms
screenshots/                  UI and export screenshots
tests/test_app.py             Automated application tests
project_report.md             Full project report
Age_Calculator_Project_Report.pdf  Generated PDF report
generate_report.py            PDF report generator from markdown
README.md                     Setup and usage instructions
```

## Prerequisites

- Python 3.10 or newer
- pip package manager
- A modern browser

## Local setup

Open a terminal in the project folder and run:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the application

Start the app:

```bash
python app.py
```

Then open the app in a browser:

```text
http://127.0.0.1:5000
```

## How to use it

1. Enter the person's name.
2. Select or type the date of birth.
3. Select the reference date for the age calculation.
4. Click the calculate button.
5. Review the result and recent history.
6. Export the result as PDF, Excel, Word, or text.

## Testing

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The tests cover:
- valid calculation flow
- invalid input handling
- date ordering checks
- leap-year cases
- export output generation
- named file export behavior
- unsupported format validation

## Screenshots

The interface and export screenshots are available in the screenshots folder and are also referenced in the project report.

## Report generation

A PDF project report can be generated with:

```bash
python generate_report.py
```

This creates:

```text
Age_Calculator_Project_Report.pdf
```

## Deployment

The project includes a Render configuration for deployment. It can also be started in a hosting environment using:

```bash
gunicorn app:app
```

## Data privacy note

Calculation history is stored in the browser's local storage only. It is not sent to a server unless the user submits a calculation or performs an export.

## Submission notes

This project is prepared for a course submission and includes source code, runnable setup instructions, and a project report. The final GitHub repository should be set to public before submission and must use the required URL format from the course instructions.

## References

- [project_report.md](project_report.md)
- [Age_Calculator_Project_Report.pdf](Age_Calculator_Project_Report.pdf)
