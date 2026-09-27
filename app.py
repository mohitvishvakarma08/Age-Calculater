from datetime import date
from io import BytesIO
import calendar
import re

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)


class AgeGroupKNN:
    def fit(self, samples, labels):
        self.samples = samples
        self.labels = labels
        return self

    def predict(self, samples):
        predictions = []
        for sample in samples:
            nearest_index = min(
                range(len(self.samples)),
                key=lambda index: abs(self.samples[index][0] - sample[0]),
            )
            predictions.append(self.labels[nearest_index])
        return predictions


def build_age_group_model():
    training_ages = [[age] for age in range(0, 121)]
    training_labels = [
        "Child" if age <= 12 else
        "Teenager" if age <= 19 else
        "Adult" if age <= 59 else
        "Senior"
        for age in range(0, 121)
    ]
    model = AgeGroupKNN()
    model.fit(training_ages, training_labels)
    return model


AGE_GROUP_MODEL = build_age_group_model()


def predict_age_group(years):
    return str(AGE_GROUP_MODEL.predict([[years]])[0])


def get_request_data():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Please provide a JSON object.")
    return data


def parse_iso_date(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Please provide a valid {field_name} date.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Please provide a valid {field_name} date in YYYY-MM-DD format.") from error


def calculate(birth, end):
    if end < birth:
        raise ValueError("The calculation date cannot be before the date of birth.")

    years = end.year - birth.year
    months = end.month - birth.month
    anniversary_day = birth.day
    if birth.month == 2 and birth.day == 29 and not calendar.isleap(end.year):
        anniversary_day = 28
    days = end.day - anniversary_day

    if days < 0:
        months -= 1
        previous_month = end.month - 1 or 12
        previous_year = end.year if end.month > 1 else end.year - 1
        days += calendar.monthrange(previous_year, previous_month)[1]

    if months < 0:
        years -= 1
        months += 12

    elapsed_days = (end - birth).days
    next_year = end.year if (end.month, end.day) < (birth.month, anniversary_day) else end.year + 1
    birthday_day = min(birth.day, calendar.monthrange(next_year, birth.month)[1])
    next_birthday = date(next_year, birth.month, birthday_day)
    days_until = (next_birthday - end).days

    return {
        "age": {"years": years, "months": months, "days": days},
        "age_group": predict_age_group(years),
        "born_on": birth.strftime("%A"),
        "next_birthday": f"{days_until} days",
        "birthday_date": next_birthday.strftime("%B %d, %Y"),
        "totals": {
            "months": years * 12 + months,
            "weeks": elapsed_days // 7,
            "days": elapsed_days,
            "hours": elapsed_days * 24,
            "minutes": elapsed_days * 24 * 60,
        },
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        today=date.today().strftime("%d/%m/%Y"),
        today_iso=date.today().isoformat(),
    )


@app.post("/api/calculate")
def calculate_route():
    try:
        data = get_request_data()
        birth = parse_iso_date(data.get("birth"), "birth")
        end = parse_iso_date(data.get("end"), "calculation")
        result = calculate(birth, end)
        name = data.get("name", "")
        if not isinstance(name, str):
            raise ValueError("Name must be text.")
        result["name"] = name.strip()
        result["birth_date"] = birth.strftime("%d/%m/%Y")
        result["end_date"] = end.strftime("%d/%m/%Y")
        return jsonify(result)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/export")
def export_route():
    try:
        data = get_request_data()
        file_type = data.get("type", "txt")
        if not isinstance(file_type, str):
            raise ValueError("Export type must be text.")
        file_type = file_type.lower()
        if file_type not in {"txt", "xlsx", "docx", "pdf"}:
            raise ValueError("Unsupported file format.")

        entered_name = data.get("name", "")
        if not isinstance(entered_name, str):
            raise ValueError("Name must be text.")
        entered_name = entered_name.strip()
        age = data.get("age")
        totals = data.get("totals")
        if not isinstance(age, dict) or not all(key in age for key in ("years", "months", "days")):
            raise ValueError("Calculation age data is incomplete.")
        if not isinstance(totals, dict) or not all(key in totals for key in ("months", "weeks", "days", "hours", "minutes")):
            raise ValueError("Calculation totals are incomplete.")
        if not all(isinstance(age[key], int) and not isinstance(age[key], bool) for key in ("years", "months", "days")):
            raise ValueError("Calculation age values must be integers.")
        if not isinstance(data.get("age_group"), str) or not data["age_group"].strip():
            raise ValueError("Age-group prediction is missing.")
        if not all(isinstance(totals[key], int) and not isinstance(totals[key], bool) for key in ("months", "weeks", "days", "hours", "minutes")):
            raise ValueError("Calculation totals must be integers.")
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    report_name = (entered_name[:1].upper() + entered_name[1:]) if entered_name else "User"
    report_title = f"{report_name}'s age"
    rows = [
        ("Name", data.get("name") or "—"),
        ("Date of birth", data.get("birth_date", "")),
        ("Calculate age on", data.get("end_date", "")),
        ("Age", f'{age["years"]} years, {age["months"]} months, {age["days"]} days'),
        ("AI age group", data["age_group"]),
        ("Born on", data.get("born_on", "")),
        ("Next birthday", data.get("next_birthday", "")),
        ("Birthday date", data.get("birthday_date", "")),
    ]
    rows.extend((f"Total {key.title()}", f"{int(value):,}") for key, value in totals.items())

    output = BytesIO()
    filename = re.sub(r'[<>:"/\\|?*]', "", report_name).rstrip(". ") or "User"
    filename = f"{filename}'s age"

    try:
        if file_type == "txt":
            detail_width = max(len("Details"), *(len(str(key)) for key, _ in rows))
            result_width = max(len("Result"), *(len(str(value)) for _, value in rows))
            separator = f"+{'-' * (detail_width + 2)}+{'-' * (result_width + 2)}+"
            table_lines = [
                report_title.upper(),
                "",
                separator,
                f"| {'Details'.ljust(detail_width)} | {'Result'.ljust(result_width)} |",
                separator,
            ]
            table_lines.extend(
                f"| {str(key).ljust(detail_width)} | {str(value).ljust(result_width)} |"
                for key, value in rows
            )
            table_lines.append(separator)
            output.write("\n".join(table_lines).encode())
            mimetype, extension = "text/plain", "txt"
        elif file_type == "xlsx":
            from openpyxl import Workbook
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Age Calculation"
            sheet.append(["Details", "Result"])
            for row in rows:
                sheet.append(list(row))
            workbook.save(output)
            mimetype, extension = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
        elif file_type == "docx":
            from docx import Document
            document = Document()
            document.add_heading(report_title, 0)
            for key, value in rows:
                document.add_paragraph(f"{key}: {value}")
            document.save(output)
            mimetype, extension = "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"
        elif file_type == "pdf":
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

            styles = getSampleStyleSheet()
            document = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=0.6 * inch,
                leftMargin=0.6 * inch,
                topMargin=0.6 * inch,
                bottomMargin=0.6 * inch,
            )
            table_rows = [["Details", "Result"]]
            table_rows.extend(
                [Paragraph(str(key), styles["BodyText"]), Paragraph(str(value), styles["BodyText"])]
                for key, value in rows
            )
            table = Table(table_rows, colWidths=[2.1 * inch, 4.8 * inch], repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            document.build([
                Paragraph(report_title, styles["Title"]),
                Spacer(1, 12),
                table,
            ])
            mimetype, extension = "application/pdf", "pdf"
        else:
            return jsonify({"error": "Unsupported file format."}), 400
    except ImportError as error:
        return jsonify({"error": f"Install the export package first: {error}"}), 500

    output.seek(0)
    return send_file(
        output,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"{filename}.{extension}",
    )


if __name__ == "__main__":
    app.run(debug=True)