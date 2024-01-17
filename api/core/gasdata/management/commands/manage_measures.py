from django.core.management.base import BaseCommand

from datetime import datetime, timedelta
import pandas as pd
from core.stationdata.models import MOVMEDTANQ, Tanque
import logging

class Command(BaseCommand):
    help = 'Generate a CSV to track MOVMEDTANQ records for each Tanque daily'

    def handle(self, *args, **kwargs):
        logging.basicConfig(filename='movmedtanq_tracking_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info("Starting MOVMEDTANQ record tracking")

        # Generate the report
        report = self.generate_movmedtanq_report()
        
        # Saving the report to CSV
        csv_filename = 'movmedtanq_report.csv'
        logging.info(f"Report saved to {csv_filename}")



    def generate_movmedtanq_report(self):
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        year, month, day = yesterday.year, yesterday.month, yesterday.day

        # Fetch all Tanques
        tanques = Tanque.objects.all()

        # Prepare the DataFrame
        columns = ['ESTACION', 'TANQUE'] + [f"{day}/{month}/{year}" for day in range(1, day+1)]
        report_data = []
        missing_stations = []

        for tanque in tanques:
            row = {'ESTACION': tanque.Estacion_id, 'TANQUE': tanque.Numero}
            for day in range(1, day+1):
                try:
                    date = datetime(year, month, day)
                except ValueError:
                    # Day does not exist in this month
                    continue

                exists = MOVMEDTANQ.objects.filter(TANQUE_ID=tanque.Numero, ESTACION=tanque.Estacion, FECHA=date).exists()
                row[f"{day}/{month}/{year}"] = 1 if exists else 0
                if not exists and date == yesterday:
                    missing_stations.append(tanque.Estacion_id)

            report_data.append(row)

        # Remove duplicates from missing stations
        missing_stations = list(set(missing_stations))

        # Log missing stations
        if missing_stations:
            missing_stations_str = ','.join(map(str, missing_stations))
            log_message = f"{yesterday.strftime('%Y-%m-%d %H:%M')} Estaciones faltantes: {missing_stations_str}"
            logging.info(log_message)
            print(log_message)  # Print in terminal

        report = pd.DataFrame(report_data, columns=columns)
        return report