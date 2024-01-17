from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import os

# Import your custom report generation functions
from core.gasdata.management.actions.medidas_registro import fetch_tanks_tabcub, register_tank_measurements  
import json
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import pandas as pd

from core.gasdata.REPORTS.report_daily_allstations import *
from core.gasdata.REPORTS.report_monthly_money import *
from core.gasdata.REPORTS.report_monthly_productstation import *
from core.gasdata.REPORTS.report_monthly_productstation_consolidated import *
from core.gasdata.REPORTS.report_monthly_productconsolidated import *
from core.gasdata.DB.db_config import *

class ReportViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling gas station reports.
    """

    def create_response_file(self, excel_content, file_name):
        """
        Create an HttpResponse with a BytesIO object for Excel file download.
        """
        response = HttpResponse(excel_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    @action(detail=False, methods=['get'])
    def generate_daily_report(self, request):
        date_filter = request.query_params.get('date')

        # Convert date_filter string to datetime object
        if date_filter:
            try:
                date_filter = pd.to_datetime(date_filter)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate dataframes
        processed_station_data, efectivo_df = generate_daily_report_df(get_inventory_data_df(), get_financial_data_df(), date_filter)

        # Convert efectivo_df to a dictionary for easy access
        efectivo_dict = efectivo_df.set_index('ESTACION').T.to_dict('list')

        # Iterate over processed_station_data to add PANAMERICANO and SUPER values
        for station_id, station_df in processed_station_data.items():
            if station_id in efectivo_dict:
                # Add PANAMERICANO and SUPER values as new columns
                station_df['PANAMERICANO'] = efectivo_dict[station_id][0]
                station_df['SUPER'] = efectivo_dict[station_id][1]
                processed_station_data[station_id] = station_df

        # Convert each DataFrame to JSON format
        for key, value in processed_station_data.items():
            if isinstance(value, pd.DataFrame):
                processed_station_data[key] = value.to_json(orient='records')

        processed_station_data_json = json.dumps(processed_station_data)

        return Response(processed_station_data_json)
    
    @action(detail=False, methods=['get'])
    def generate_monthly_money_report(self, request):
        year_str = request.query_params.get('year')
        month_str = request.query_params.get('month')

        # Convert year and month to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            return Response({"error": "Invalid year or month format. They should be integers."}, status=status.HTTP_400_BAD_REQUEST)

        reporte_efectivo_df, report_headers = generate_reporte_efectivo_df(get_financial_data_df(), year, month)

        return Response(reporte_efectivo_df.to_json(orient='records'), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def generate_product_station_report(self, request):
        year_str = request.query_params.get('year')
        month_str = request.query_params.get('month')

        # Convert year and month to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            return Response({"error": "Invalid year or month format. They should be integers."}, status=status.HTTP_400_BAD_REQUEST)
        estacion_id = request.query_params.get('estacion_id')
        product_id = request.query_params.get('product_id')
        final_df, report_headers = create_report(get_inventory_data_df(), create_estaciones_df(), create_productos_df(), create_empresa_df(), month, year, estacion_id, product_id)
        final_df['FECHA']=final_df['FECHA'].astype(str)


        return Response(final_df.to_json(orient='records'), status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'])
    def generate_station_products_report(self, request):
        year_str = request.query_params.get('year')
        month_str = request.query_params.get('month')

        # Convert year and month to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            return Response({"error": "Invalid year or month format. They should be integers."}, status=status.HTTP_400_BAD_REQUEST)
        estacion_id = request.query_params.get('estacion_id')
        final_df, report_headers = create_report_products(get_inventory_data_df(), create_estaciones_df(), create_productos_df(), create_empresa_df(), month, year, estacion_id)



        return Response(final_df.to_json(orient='records'), status=status.HTTP_200_OK)

    # Methods for Excel report generation
    @action(detail=False, methods=['get'])
    def download_daily_report(self, request):
        date_filter = request.query_params.get('date')
        if date_filter:
            try:
                date_filter = pd.to_datetime(date_filter)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        excel_content = output_to_excel_daily_report(get_inventory_data_df(), get_financial_data_df(), date_filter)
        return self.create_response_file(excel_content, "daily_report.xlsx")
    
    @action(detail=False, methods=['get'])
    def download_monthly_money_report(self, request):
        year_str = request.query_params.get('year')
        month_str = request.query_params.get('month')

        # Convert year and month to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            return Response({"error": "Invalid year or month format. They should be integers."}, status=status.HTTP_400_BAD_REQUEST)
        re_df, report_headers = generate_reporte_efectivo_df(get_financial_data_df(), year, month)
        excel_content = output_efectivo_to_excel(re_df, report_headers)
        return self.create_response_file(excel_content, "monthly_money_report.xlsx")
    
    @action(detail=False, methods=['get'])
    def download_product_station_report(self, request):
        year_str = request.query_params.get('year')
        month_str = request.query_params.get('month')
        # Convert year and month to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            return Response({"error": "Invalid year or month format. They should be integers."}, status=status.HTTP_400_BAD_REQUEST)
        estacion_id = request.query_params.get('estacion_id')
        product_id = request.query_params.get('product_id')
        final_df, report_headers = create_report(get_inventory_data_df(), create_estaciones_df(), create_productos_df(), create_empresa_df(), month, year, estacion_id, product_id)
        excel_content = output_report_to_excel(final_df, report_headers)
        return self.create_response_file(excel_content, "product_station_report.xlsx")
    

    @action(detail=False, methods=['get'])
    def download_consolidated_report(self, request):
        year_str = request.query_params.get('year')
        month_str = request.query_params.get('month')

        # Convert year and month to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            return Response({"error": "Invalid year or month format. They should be integers."}, status=status.HTTP_400_BAD_REQUEST)
        excel_content = output_reportconsolidated_to_excel(get_inventory_data_df(), create_estaciones_df(), create_productos_df(), create_empresa_df(), month, year)
        return self.create_response_file(excel_content, "consolidated_report.xlsx")
    """
    @action(detail=False, methods=['get'])
    def cubtables(self, request):
        data = fetch_data_tabcub()
        return Response(status=status.HTTP_200_OK)
    """
class RegistroMedidasViewSet(viewsets.ViewSet):

    """
    A ViewSet for handling actions.
    """
    @action(detail=False, methods=['get'])
    def getstationtanks(self, request):
        station = request.query_params.get('station')
        dict_Tanks = fetch_tanks_tabcub(station)
        return Response(json.dumps(dict_Tanks),status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['post'])
    def registermedidas(self, request):
        data = json.loads(request.body)

        # Validate that the required fields are in the data
        required_fields = {'date', 'station', 'tanks'}
        if not all(field in data for field in required_fields):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        
        result, error = register_tank_measurements(data)

        if error:
            return Response(error, status=error.get('status', status.HTTP_400_BAD_REQUEST))

        return Response(result, status=status.HTTP_201_CREATED)

 #http://localhost:8000/api/stationdata/medidas/getstationtanks/?station=016

from rest_framework import viewsets
from rest_framework.response import Response
import subprocess
from concurrent.futures import ThreadPoolExecutor

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from concurrent.futures import ThreadPoolExecutor
import subprocess

class UpdateDataViewSet(viewsets.ViewSet):

    def run_command(self, command):
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.execute_command, command)
        return Response({"message": f"Execution of '{command}' started"})

    def execute_command(self, command):
        try:
            subprocess.run(['python', 'manage.py', command], check=True)
            return f"'{command}' executed successfully"
        except subprocess.CalledProcessError as e:
            return f"Execution of '{command}' failed: {e}"

    def list(self, request):
        # Default action for the viewset
        return self.run_command('update_data')

    @action(detail=False, methods=['get'])
    def update_inventory(self, request):
        # Separate action for updating inventory
        return self.run_command('update_inventory')

