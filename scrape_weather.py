"""
Name: Noah Pagtakhan
Date: 2025-11-10
Description:
    Weather scraper to fetch weather data from the canada climate data website.
"""

from html.parser import HTMLParser
from urllib.request import urlopen
from datetime import date
import logging
 
class WeatherScraper(HTMLParser):
 
    def __init__(self):
        """initial method to set variables"""
        super().__init__()
        self.rows = []
        self._in_table = False
        self._cur_row = []
        self._capture = False
 
    def handle_starttag(self, tag, attrs):
        """checks to see if we are in a table tag with the id of data table"""
        attrs_dict = dict(attrs)
        if tag == "table" and "data-table" in attrs_dict.get("class", ""):
            self._in_table = True
        if self._in_table and tag == "tr":
            self._cur_row = []
        if self._in_table and tag in ("td", "th"):
            self._capture = True
 
    def handle_endtag(self, tag):
        """if once we are finished with the data, if we see another table tag, we close our "table" connection."""
        if self._in_table and tag in ("td", "th"):
            self._capture = False
        if self._in_table and tag == "tr" and self._cur_row:
            self.rows.append(self._cur_row)
        if tag == "table" and self._in_table:
            self._in_table = False
 
    def handle_data(self, data):
        """we handle the data by removing any blank spaces and extra text such as "\n" """
        if self._capture:
            self._cur_row.append(data.strip())
 
    def scrape_month(self, url: str) -> dict:
        """this method scrapes the weather data of the particular month, and stores in a dictionary"""
        html = urlopen(url).read().decode("utf-8", errors="ignore")
        """decodes any raw html into strings which allows python to process normally"""
        self.rows, self._in_table = [], False
        self.feed(html)
 
        out = {}
        for row in self.rows:
            """This checksif the min, max, and mean/avg temps are truly digits. 
            it will get rid of the decimal point and the negative to check the digits itself.
            if it is a digit, it will convert to a float, if it is not, do not store."""
            try:
                day = row[0]
                if not day.isdigit():
                    continue
                out[int(day)] = {
                    "min": float(row[2]) if row[2].replace('.', '', 1).lstrip('-').isdigit() else None,
                    "max": float(row[3]) if row[3].replace('.', '', 1).lstrip('-').isdigit() else None,
                    "mean": float(row[4]) if row[4].replace('.', '', 1).lstrip('-').isdigit() else None,
                }
            except Exception as ex:
                logging.exception("Row parse error: %s", row)
        return out
 
    def scrape_back_in_time(
            self, url_tmpl: str, station_id: int, 
            start: date | None = None, 
            max_months: int | None = None
            ) -> dict:
        """this method starts from either a given date, or current date then scrapes back in time"""
        today = start or date.today()
        year, month = today.year, today.month
        all_data = {}
 
        while True:
            url = url_tmpl.format(sid=station_id, year=year, month=month)
            """once given url, begin to scrape the month"""
            month_data = self.scrape_month(url)
            if not month_data:
                break
            for day, vals in month_data.items():
                """converts to iso to store into the database"""
                iso = f"{year:04d}-{month:02d}-{day:02d}"
                all_data[iso] = vals
 
            month -= 1
            if month == 0:
                """once month has reached 0, move back to december and subtract a year."""
                month, year = 12, year - 1
 
            if max_months and len(all_data) >= max_months * 28:
                break
 
        return all_data