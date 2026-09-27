from datetime import date
from io import BytesIO
import calendar

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)


def calculate(birth, end):
    if end < birth:
        raise ValueError("The calculation date cannot be before the date of birth.")

    years = end.year - birth.year
    months = end.month - birth.month
    days = end.day - birth.day

    if days < 0:
        months -= 1
        previous_month = end.month - 1 or 12
        previous_year = end.year if end.month > 1 else end.year - 1
        days += calendar.monthrange(previous_year, previous_month)[1]

    if months < 0:
        years -= 1
        months += 12

    elapsed_days = (end - birth).days
    next_year = end.year if (end.month, end.day) < (birth.month, birth.day) else end.year + 1
    birthday_day = min(birth.day, calendar.monthrange(next_year, birth.month)[1])
    next_birthday = date(next_year, birth.month, birthday_day)
    days_until = (next_birthday - end).days

    return {
        "age": {"years": years, "months": months, "days": days},
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
        data = request.get_json()
        birth = date.fromisoformat(data["birth"])
        end = date.fromisoformat(data["end"])
        result = calculate(birth, end)
        result["name"] = data.get("name", "").strip()
        result["birth_date"] = birth.strftime("%d/%m/%Y")
        result["end_date"] = end.strftime("%d/%m/%Y")
        return jsonify(result)
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error) or "Please enter valid dates."}), 400


@app.post("/api/export")
def export_route():
    data = request.get_json()
    file_type = data.get("type", "txt").lower()
    rows = [
        ("Name", data.get("name") or "—"),
        ("Date of birth", data.get("birth_date", "")),
        ("Calculate age on", data.get("end_date", "")),
        ("Age", f'{data["age"]["years"]} years, {data["age"]["months"]} months, {data["age"]["days"]} days'),
        ("Born on", data.get("born_on", "")),
        ("Next birthday", data.get("next_birthday", "")),
        ("Birthday date", data.get("birthday_date", "")),
    ]
    rows.append(("", ""))
    rows.append(("Total time", ""))
    rows.extend((f"Total {key.title()}", f"{int(value):,}") for key, value in data["totals"].items())

    output = BytesIO()
    filename = "age-calculation"

    try:
        if file_type == "txt":
            detail_width = max(len("Details"), *(len(str(key)) for key, _ in rows))
            result_width = max(len("Result"), *(len(str(value)) for _, value in rows))
            separator = f"+{'-' * (detail_width + 2)}+{'-' * (result_width + 2)}+"
            table_lines = [
                "AGE CALCULATOR",
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
            document.add_heading("Age Calculator", 0)
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
            total_time_row = 1 + next(index for index, row in enumerate(rows) if row == ("Total time", ""))
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
                ("SPAN", (0, total_time_row), (1, total_time_row)),
                ("BACKGROUND", (0, total_time_row), (-1, total_time_row), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, total_time_row), (-1, total_time_row), colors.HexColor("#1e3a8a")),
                ("FONTNAME", (0, total_time_row), (-1, total_time_row), "Helvetica-Bold"),
            ]))
            document.build([
                Paragraph("Age Calculator", styles["Title"]),
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