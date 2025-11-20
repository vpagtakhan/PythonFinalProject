from scrape_weather import WeatherScraper
from db_operations import DBOperations
from dbcm import DBCM
from plot_operations import PlotOperations
from pprint import pprint

db = DBOperations(db_name="weather.db")

scraper = WeatherScraper()
plotter = PlotOperations()

# url_template = (
#         "https://climate.weather.gc.ca/climate_data/daily_data_e.html?"
#         "StationID={sid}&timeframe=2&StartYear=1840&EndYear={year}&Day=1&Year={year}&Month={month}"
#     )

# scraped_data = scraper.scrape_back_in_time(url_template, station_id=27174)

# db.purge_data

# print(f"Scraped {len(scraped_data)} records from Environment Canada.")

# db.save_weather_data("Winnipeg", scraped_data)
# print("Saved data into weather database")

# fetched_data = db.fetch_data("2020")

# pprint(fetched_data)

# plotter.box_plot_mean_temps(2020, 2024)
plotter.line_plot_mean_temps(2025, 10)

