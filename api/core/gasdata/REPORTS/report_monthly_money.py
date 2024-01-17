import pandas as pd
from datetime import datetime
import io
##########################################################################################################################
################################################################   REPORTE POR ESTACIÓN MENSUAL  ################################################################################################import pandas as pd
###################################################################################################################################################################import pandas as pd
def generate_reporte_efectivo_df(efectivo_df, year, month):
    reporte_efectivo_df = pd.DataFrame()
    efectivo_df = efectivo_df.drop(columns=['id'])
    for station in efectivo_df[efectivo_df['SUPER'] > 0].ESTACION.unique().tolist():
        reporte_efectivo_df['FECHA'] = efectivo_df['FECHA'].unique().tolist()
        reporte_efectivo_df = reporte_efectivo_df.merge(
            efectivo_df[efectivo_df['ESTACION'] == station].drop(columns=['PANAMERICANO', 'ESTACION']).rename(columns={"SUPER": f"AGUILA {station}"}),
            on=['FECHA'], how='outer'
        )
    
    reporte_efectivo_df = reporte_efectivo_df[(reporte_efectivo_df['FECHA'].dt.month == month) &
                                              (reporte_efectivo_df['FECHA'].dt.year == year)].fillna(0)

    # Get the month name correctly
    month_name = datetime(year, month, 1).strftime('%B').upper()
    report_headers = [
        f"CORPORATIVO ÁGUILA",
        f"REPORTE DE VENTAS SUPER",
        f"{month_name} - {year}"
    ]

    return reporte_efectivo_df, report_headers

def output_efectivo_to_excel(re_df, report_headers):
    output = io.BytesIO()
    if re_df is not None:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            re_df.to_excel(writer, sheet_name='Report', startrow=4, header=True, index=False)

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
            for row_num, data in enumerate(re_df.values):
                for col_num, cell_value in enumerate(data):
                    # Apply number format starting from 'Ventas' column
                    cell_format = custom_num_format if col_num > 0 else body_format
                    worksheet.write(row_num + 5, col_num, cell_value, cell_format)

            # Write the report headers above the table with formatting and centering
            for row_num, header in enumerate(report_headers):
                worksheet.merge_range(row_num, 0, row_num, len(re_df.columns) - 1, header, header_format)

            # Adjust the column widths based on the longest entry in each column
            for col_num, column in enumerate(re_df.columns):
                max_len = max(
            re_df[column].astype(str
                        ).apply(len
                        ).max(),  # len of largest item
                        len(str(column)))  # len of column name/header
                worksheet.set_column(col_num, col_num, max_len + 2)  # add a little extra space
        output.seek(0)
        return output

