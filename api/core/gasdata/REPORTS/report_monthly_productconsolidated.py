
import pandas as pd
from datetime import datetime
import io
####################################################################################################################################################################################################################################################
################################################################    REPORTE DE PRODUCTOS POR ESTACIÓN  ################################################################################################i##########################################################################################################################
#############################################################################################################################################################################################################################################################################################



def create_report_products(df, estaciones_df, productos_df, empresa_df, month, year, estacion_id):
    try:
        # Convert FECHA to datetime and filter the DataFrame
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        month_df = df[(df['FECHA'].dt.month == month) & (df['FECHA'].dt.year == year) & (df['ESTACION'] == estacion_id)]

        # Check for NaN values
        if month_df.isnull().values.any():
            return None, ["Row contains NaN values"]

        # Retrieve station and company names
        estacion_name = estaciones_df.loc[estaciones_df['ESTACION_ID'] == estacion_id, 'ESTACION_NOMBRE'].iat[0]
        empresa_name = empresa_df.loc[empresa_df['EMPRESA_ID'] == estaciones_df.loc[estaciones_df['ESTACION_ID'] == estacion_id, 'COMPANY_ID'].iat[0], 'EMPRESA_RAZONSOCIAL'].iat[0]
        month_name = datetime(year, month, 1).strftime('%B').upper()

        # Group by 'FECHA' and 'PRODUCTO', sum 'LTSVENTA', and pivot the DataFrame
        final_df = month_df.groupby(['FECHA', 'PRODUCTO'])['LTSVENTA'].sum().unstack().fillna(0)

        # Reset index to turn 'FECHA' back into a column
        final_df.reset_index(inplace=True)
        
        # Calculate total sales for each product and add a total row
        totals = final_df.drop(columns=['FECHA']).sum().rename('TOTAL')
        total_row = pd.DataFrame([totals], index=['TOTAL'])
        final_df = pd.concat([final_df, total_row])
        final_df.to_csv('ventas.csv')
        # Create report headers
        report_headers = [f"{estacion_name}", f"{empresa_name}", f"{month_name} {year}"]

        return final_df, report_headers

    except Exception as e:
        return None, [str(e)]
