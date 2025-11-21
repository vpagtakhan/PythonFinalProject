"""
Name: Noah Pagtakhan
Date: 2025-11-14
Description:
    Database for final project that stores weather data scraped from the WeatherScraper class
"""
from dbcm import DBCM

class DBOperations:
    """Database class to insert scraped weather data and prepare data to be used for plotting"""

    def __init__(self, db_name="weather.db"):
        """initialize database"""
        self.db_name = db_name
        self._initialize_db()

    def _initialize_db(self):
        """Creating the database if it does not exist already"""
        with DBCM(self.db_name) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           sample_date TEXT NOT NULL,
                           location TEXT NOT NULL,
                           min_temp REAL,
                           max_temp REAL,
                           avg_temp REAL,
                           UNIQUE(sample_date, location)
                           )"""
        )            
    def save_weather_data(self, location: str, data: dict):
        """Saving scraped weather data and inserting into database table, 
        if there are duplicates; we ignore them."""
        with DBCM(self.db_name) as cursor:
            for sample_date, temps in data.items():
                cursor.execute("""
                            INSERT OR IGNORE INTO weather
                            (sample_date, location, min_temp, max_temp, avg_temp)
                            VALUES(?, ?, ?, ?, ?)""", (
                                sample_date,
                                location,
                                temps.get("min"),
                                temps.get("max"),
                                temps.get("avg") or temps.get("mean"),
                            ))
    def purge_data(self):
        """purge existing weather data to prepare for new data"""
        with DBCM(self.db_name) as cursor:
            cursor.execute("DELETE FROM weather")

    def fetch_all_as_dict(self):
        """preparing data to display as a dictionary of dictionaries"""
        with DBCM(self.db_name) as cursor:
            cursor.execute(""""SELECT sample_date, location, min_temp, max_temp, avg_temp
                           FROM weather 
                           ORDER BY sample_date ASC""")
            rows = cursor.fetchall()

            grouped = {}

            for row in rows:
                sample_date, location, min_temp, max_temp, avg_temp = row

                year = sample_date[:4]

                if year not in grouped:
                    grouped[year] = {}

                grouped[year][sample_date] = {
                    "location": location,
                    "min_temp": min_temp,
                    "max_temp": max_temp,
                    "avg_temp": avg_temp
                }
        return grouped
    def fetch_mean_month(self, year: int) -> dict[int, list[float]]:
        """fetch daily temps for 1 month of a specific year"""        
        result = {m: [] for m in range(1,13)}
        
        with DBCM(self.db_name) as cursor:
            cursor.execute("""
            SELECT sample_date, avg_temp
            FROM WEATHER
            WHERE strftime('%Y', sample_date) = ?
            ORDER BY sample_date ASC;"""
        , (str(year),))            
            rows = cursor.fetchall()

            for sample_date, avg_temp in rows:
                if avg_temp is None:
                    continue

                month = int(sample_date[5:7])
                result[month].append(avg_temp)

        return result
    
    def fetch_mean_year_range(self, start_year: int, end_year: int):
        """fetch temperatures based on year range (ex. 2020-2024)"""

        with DBCM(self.db_name) as cursor:
            cursor.execute("""
                SELECT
                    CAST(strftime('%Y', sample_date) AS INT) AS year,
                    AVG(avg_temp) AS mean_temp
                FROM weather
                WHERE CAST(strftime('%Y', sample_date)AS INTEGER)
                    BETWEEN ? AND ?
                GROUP BY year
                ORDER BY year ASC;
                """, (start_year, end_year))            
            return cursor.fetchall()