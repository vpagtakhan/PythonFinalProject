from flask import Flask, render_template, request, send_file
from db_operations import DBOperations
from scrape_weather import WeatherScraper
from plot_operations import PlotOperations
import io
import csv
import json
import matplotlib
matplotlib.use("Agg")

db = DBOperations(db_name="weather.db")
scraper = WeatherScraper()
plotter = PlotOperations("weather.db")
app = Flask(__name__)

url_template = (
        "https://climate.weather.gc.ca/climate_data/daily_data_e.html?"
        "StationID={sid}&timeframe=2&StartYear=1840&EndYear={year}&Day=1&Year={year}&Month={month}"
    )

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

@app.route("/update_data")
def update_data():
    scraped_data = scraper.scrape_back_in_time(url_template, station_id=27174, max_months=1)

    if not scraped_data:
        return "No new data has been returned from Environment Canada.", 500
    
    db.save_weather_data("Winnipeg", scraped_data)
    
    return f"Weather data updated. {len(scraped_data)} daily records have been saved."

@app.route("/plot_box")
def plot_box():
    start_year = request.args.get("start_year")
    end_year = request.args.get("end_year")

    if not start_year or not end_year:
        return "Missing start and end year", 400
    
    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except ValueError:
        return "Invalid year values", 400
    
    buf = plotter.box_to_png(start_year, end_year)
    if buf is None:
        return f"No data found for {start_year}-{end_year}.", 404
    
    return send_file(buf, mimetype="image/png")

@app.route("/plot_line")
def plot_line():
    year = request.args.get("year")
    month = request.args.get("month")

    if not year or not month:
        return "Missing year or month", 400
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return "Invalid year or month", 400
    
    if month < 1 or month > 12:
        return "Mont must be between 1 and 12", 400
    
    buf = plotter.line_to_png(year, month)
    if buf is None:
        return f"No data found for {year}-{month:02d}", 404
    
    return send_file(buf, mimetype="image/png")

if __name__ == '__main__':
    app.run(debug=True, port=5000)