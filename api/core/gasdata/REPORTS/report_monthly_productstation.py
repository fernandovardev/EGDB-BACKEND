
import pandas as pd
from datetime import datetime
import io
####################################################################################################################################################################################################################################################
################################################################    REPORTE POR ESTACIÓN POR PRODUCTO   ################################################################################################i##########################################################################################################################
#############################################################################################################################################################################################################################################################################################



def create_report(df, estaciones_df, productos_df, empresa_df, month, year, estacion_id, product_id):
    try:
        df = df.drop(columns=['id'])
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        print(estacion_id, product_id)
        
        # Calculate the first day of the specified month and year
        first_day_of_month = pd.Timestamp(year=year, month=month, day=1)

        # Subtract one day to get the last day of the previous month
        last_day_of_previous_month = first_day_of_month - pd.Timedelta(days=1)

        # Filter out the row for the last day of the previous month
        last_day_df = df[(df['FECHA'] == last_day_of_previous_month) & 
                         (df['ESTACION'] == estacion_id) & 
                         (df['PRODUCTO'] == product_id)].copy()

        # Filter the rest of the DataFrame for the specified month and year
        rest_of_month_df = df[(df['FECHA'].dt.month == month) & 
                              (df['FECHA'].dt.year == year) & 
                              (df['ESTACION'] == estacion_id) & 
                              (df['PRODUCTO'] == product_id)].copy()

        # Set all values to NaN in the rest_of_month_df, except 'FECHA'
        for col in last_day_df.columns:
            if col != 'FECHA' and col != 'FISICA':
                last_day_df[col] = [None]
        last_day_df['FECHA'] = 'INVENTARIO INICIAL'

        # Concatenate the last day of the previous month row with the rest of the month DataFrame
        filtered_df = pd.concat([last_day_df, rest_of_month_df])
        print(filtered_df)
        if rest_of_month_df.empty:
            return None, ["No data available for the specified filters"]

        # Check for NaN values in the final_df
        if rest_of_month_df.isnull().any(axis=1).any():
            return None, ["Row contains NaN values"]

        first_row = rest_of_month_df.iloc[0]
        # Use 'iat' for faster scalar access if you're retrieving a single value
        estacion_name = estaciones_df.loc[estaciones_df['ESTACION_ID'] == estacion_id, 'ESTACION_NOMBRE'].iat[0]
        empresa_name = empresa_df.loc[empresa_df['EMPRESA_ID'] == estaciones_df.loc[estaciones_df['ESTACION_ID'] == estacion_id, 'COMPANY_ID'].iat[0], 'EMPRESA_RAZONSOCIAL'].iat[0]
        producto_name = productos_df.loc[productos_df['PRODUCTO_ID'] == first_row['PRODUCTO'], 'PRODUCTO_NOMBRE'].iat[0]

        # Get the month name correctly
        month_name = datetime(year, month, 1).strftime('%B').upper()

        report_headers = [
            f"{estacion_name}",
            f"{empresa_name}",
            f"{producto_name}",
            f"{month_name} {year}"
        ]

        final_df = filtered_df.drop(columns=['ESTACION', 'PRODUCTO'])

        # Rename columns
        final_df.rename(columns={
            'FECHA': 'FECHA',
            'LTSVENTA': 'VENTAS',
            'LTSMOV': 'DESCARGAS',
            'VOLUMEN': 'PRUEBA DE BOMBAS',
            'EXISTENCIA_CONTABLE': 'EXISTENCIA CONTABLE',
            'FISICA': 'EXISTENCIA FISICA',
            'DIFERENCIA': 'DIFERENCIA',
            'DIFERENCIA_ACUMULADA': 'DIFERENCIA ACUMULADA'
        }, inplace=True)

        # Reorder columns to maintain the same order as before
        column_order = ['FECHA', 'VENTAS', 'DESCARGAS', 'PRUEBA DE BOMBAS', 'EXISTENCIA CONTABLE', 'EXISTENCIA FISICA', 'DIFERENCIA', 'DIFERENCIA ACUMULADA']
        final_df = final_df[column_order]

        # Calculate sums for the specified columns
        total_ventas = final_df['VENTAS'].sum()
        total_descargas = final_df['DESCARGAS'].sum()
        total_pruebas = final_df['PRUEBA DE BOMBAS'].sum()

        # Create a DataFrame with the totals
        totals_df = pd.DataFrame({
            'FECHA': ['TOTAL'],
            'VENTAS': [total_ventas],
            'DESCARGAS': [total_descargas],
            'PRUEBA DE BOMBAS': [total_pruebas],
            'EXISTENCIA CONTABLE': [None],  # You can put None or any other placeholder
            'EXISTENCIA FISICA': [None],
            'DIFERENCIA': [None],
            'DIFERENCIA ACUMULADA': [None]
        })

        # Append the totals DataFrame to the final DataFrame
        final_df = pd.concat([final_df, totals_df], ignore_index=True)

        return final_df, report_headers

    except Exception as e:
        return None, [str(e)]

def output_report_to_excel(report_df, report_headers):
    output = io.BytesIO()
    if report_df is not None:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

            report_df.to_excel(writer, sheet_name='Report', startrow=4, header=True, index=False)

            workbook = writer.book
            worksheet = writer.sheets['Report']

            # Define the header format with bold white text on a red background
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#FF0000',  # Strong red background
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })

            # Define the format for the body with borders
            body_format = workbook.add_format({'border': 1,
                                                'num_format': 'yyyy-mm-dd',})

            # Define a custom number format for 'Ventas' column (B) with a minus sign and red color for negative numbers
            custom_num_format = workbook.add_format({
                'num_format': '#,##0.00;[Red]-#,##0.00',
                'border': 1
            })

            # Apply the body format to the range of cells that contain data
            for row_num, data in enumerate(report_df.values):
                for col_num, cell_value in enumerate(data):
                    # Apply number format starting from 'Ventas' column
                    cell_format = custom_num_format if col_num > 0 else body_format
                    worksheet.write(row_num + 5, col_num, cell_value, cell_format)

            # Write the column headers with formatting
            for col_num, value in enumerate(report_df.columns.values):
                worksheet.write(3, col_num, value, header_format)

            # Write the report headers above the table with formatting and centering
            for row_num, header in enumerate(report_headers):
                worksheet.merge_range(row_num, 0, row_num, len(report_df.columns) - 1, header, header_format)

            # Adjust the column widths based on the longest entry in each column
            # Calculate the maximum column width
            max_width = 0
            for column in report_df.columns:
                max_len_in_col = max(report_df[column].astype(str).apply(len).max(),  # Length of largest item in the column
                                    len(str(column)))  # Length of column name/header
                max_width = max(max_width, max_len_in_col)

            # Adding a little extra space to max_width
            max_width += 2

            # Setting the same column width for all columns
            for col_num in range(len(report_df.columns)):
                worksheet.set_column(col_num, col_num, max_width)
        output.seek(0)
        return output
