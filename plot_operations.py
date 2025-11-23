import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from db_operations import DBOperations


class PlotOperations:
    """class that allows data from DBOperations to be used for creating box plot and line plot graphs"""

    def __init__(self, db_name = "weather.db"):
        """Calling the database to use its data"""
        self.db = DBOperations(db_name=db_name)

    def box_plot_mean_temps(self, start_year: int, end_year: int):
        """Creates a box plot for avg_temps between a year range."""

        year_to_temps = {}

        for year in range(start_year, end_year + 1):
            monthly_data = self.db.fetch_mean_month(year)

            all_temps = []
            for month, temps in monthly_data.items():
                all_temps.extend([t for t in temps if t is not None])

            if all_temps:
                year_to_temps[year] = all_temps

        print("Final aggregated data:", year_to_temps)
        
        if not year_to_temps:
            print("No temperature data found in this range.")
            return
        
        """Preparing data for plotting"""
        data_for_plot = list(year_to_temps.values())
        labels = list(year_to_temps.keys())

        plt.figure(figsize=(10,6))
        plt.boxplot(data_for_plot)
        plt.xticks(range(1, len(labels) + 1), labels)
        plt.title(f"Mean temperatures for date range: {start_year}-{end_year}")
        plt.ylabel("Mean Temperature")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()

    def box_to_png(self, start_year: int, end_year: int):

        year_to_temps = {}

        for year in range(start_year, end_year +1):
            monthly_data = self.db.fetch_mean_month(year)

            all_temps = []
            for month, temps in monthly_data.items():
                all_temps.extend([t for t in temps if t is not None])
            
            if all_temps:
                year_to_temps[year] = all_temps
        
        if not year_to_temps:
            print("No temperature data found in this range.")
            return
        
        data_for_plot = list(year_to_temps.values())
        labels = list(year_to_temps.keys())

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.boxplot(data_for_plot)
        ax.set_xticklabels(labels)
        ax.set_title(f"Mean Temperatures for date range: {start_year}-{end_year}")
        ax.set_ylabel("Mean Temperature")
        ax.grid(True, linestyle="--", alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)

        return buf

    def line_plot_mean_temps(self, year: int, month: int):
        """Uses a line plot to display daily average temps for a whole month withing a specifc year"""

        monthly_data = self.db.fetch_mean_month(year)

        if month not in monthly_data:
            print(f"No data found for year {year}-{month:02d}")
            return
        
        """preparing the data to be used in plotting"""
        temps = monthly_data[month]
        days = list(range(1, len(temps) + 1))

        plt.figure(figsize=(10, 5))
        plt.plot(days, temps, marker='o')
        plt.title(f"Daily mean temperature for {year}-{month:02d}")
        plt.xlabel("Day of Month")
        plt.ylabel("Mean Temperature")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.show()

    def line_to_png(self, year: int, month: int):

        monthly_data = self.db.fetch_mean_month(year)

        if month not in monthly_data:
            print(f"No data found for year {year}-{month:02d}")
            return
        
        """preparing the data to be used in plotting"""
        temps = monthly_data[month]
        days = list(range(1, len(temps) + 1))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(days, temps, marker='o')
        ax.set_title(f"Daily Mean Temperatures - {year}-{month:02d}")
        ax.set_xlabel("Day")
        ax.set_ylabel("Mean Temperatures")
        ax.grid(True, linestyle="--", alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)

        return buf