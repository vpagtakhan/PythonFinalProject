from html.parser import HTMLParser
from urllib.request import urlopen
from datetime import date
import logging
 
class WeatherScraper(HTMLParser):
 
    def __init__(self):
        super().__init__()
        self.rows = []
        self._in_table = False
        self._cur_row = []
        self._capture = False
 
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table" and "data-table" in attrs_dict.get("class", ""):
            self._in_table = True
        if self._in_table and tag == "tr":
            self._cur_row = []
        if self._in_table and tag in ("td", "th"):
            self._capture = True
 
    def handle_endtag(self, tag):
        if self._in_table and tag in ("td", "th"):
            self._capture = False
        if self._in_table and tag == "tr" and self._cur_row:
            self.rows.append(self._cur_row)
        if tag == "table" and self._in_table:
            self._in_table = False
 
    def handle_data(self, data):
        if self._capture:
            self._cur_row.append(data.strip())
 
    def scrape_month(self, url: str) -> dict:
        html = urlopen(url).read().decode("utf-8", errors="ignore")
        self.rows, self._in_table = [], False
        self.feed(html)
 
        out = {}
        for row in self.rows:
            try:
                day = row[0]
                if not day.isdigit():
                    continue
                out[int(day)] = {
                    "min": float(row[2]) if row[2].replace('.', '', 1).lstrip('-').isdigit() else None,
                    "max": float(row[3]) if row[3].replace('.', '', 1).lstrip('-').isdigit() else None,
                    "mean": float(row[5]) if row[5].replace('.', '', 1).lstrip('-').isdigit() else None,
                }
            except Exception as ex:
                logging.exception("Row parse error: %s", row)
        return out
 
    def scrape_back_in_time(
            self, url_tmpl: str, station_id: int, 
            start: date | None = None, 
            max_months: int | None = None
            ) -> dict:
        today = start or date.today()
        year, month = today.year, today.month
        all_data = {}
 
        while True:
            url = url_tmpl.format(sid=station_id, year=year, month=month)
            month_data = self.scrape_month(url)
            if not month_data:
                break
            for day, vals in month_data.items():
                iso = f"{year:04d}-{month:02d}-{day:02d}"
                all_data[iso] = vals
 
            month -= 1
            if month == 0:
                month, year = 12, year - 1
 
            if max_months and len(all_data) >= max_months * 28:
                break
 
        return all_data
    
 
if __name__ == "__main__":
    scraper = WeatherScraper()
    url_template = (
        "https://climate.weather.gc.ca/climate_data/daily_data_e.html?"
        "StationID={sid}&timeframe=2&StartYear=1840&EndYear={year}&Day=1&Year={year}&Month={month}"
    )
 
    print("Scraping Environment Canada weather data...")
    data = scraper.scrape_back_in_time(url_template, station_id=27174, max_months=6)
    print(f"\n{data}")