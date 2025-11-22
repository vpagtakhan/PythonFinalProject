from flask import Flask, render_template, request, send_file
from db_operations import DBOperations
import io
import csv
import json

db = DBOperations(db_name="weather.db")
app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/download_data')
def download_data():
    start_year = request.args.get("start_year")
    end_year = request.args.get("end_year")
    file_format = request.args.get("format", "csv")

    if not start_year or not end_year:
        return "Missing start_year or end_year", 400
    
    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except ValueError:
        return "Invalid year values", 400
    
    rows = db.fetch_mean_year_range(start_year, end_year)

    if not rows:
        return "No data found for that year range.", 404
    
    if file_format == "json":
        return generate_json(rows, start_year, end_year)
    else:
        return generate_csv(rows, start_year, end_year)
    
def generate_csv(rows, start_year: int, end_year: int):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["year", "mean_temp"])

    for year, mean_temp in rows:
        writer.writerow([year, mean_temp])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"weather_{start_year}_{end_year}.csv",
    )

def generate_json(rows, start_year: int, end_year: int):
    data = [{"year": year, "mean_temp": mean_temp} for year, mean_temp in rows]
    json_bytes = json.dumps(data, indent=4).encode("utf-8")

    return send_file(
        io.BytesIO(json_bytes),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"weather_name_{start_year}_{end_year}.json",
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)