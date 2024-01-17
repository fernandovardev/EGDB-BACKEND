from datetime import datetime
import pandas as pd
from core.gasdata.REPORTS.report_monthly_productstation import create_report
from core.gasdata.DB.db_config import create_stock_df, data
import io
import numpy as np  # Import numpy to handle NaN and Inf values

####################################################################################################################################################################################################################################################
################################################################   REPORTE POR PRODUCTO CONSOLIDADO  ##########################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################
stockdf=create_stock_df(data)
def output_reportconsolidated_to_excel(df, estaciones_df,productos_df, empresa_df, month, year):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        workbook = writer.book
        worksheet = workbook.add_worksheet('Consolidated Report')
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#FF0000',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        diesel_header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#000000',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        magna_header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#008000',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        premium_header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#FF0000',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        body_format = workbook.add_format({'border': 1, 'num_format': 'yyyy-mm-dd'})
        custom_num_format = workbook.add_format({
            'num_format': '#,##0.00;[Red]-#,##0.00',
            'border': 1
        })

        current_row = 0

        for estacion_id in stockdf.ESTACION.unique():
            for product_id in stockdf.PRODUCTO.unique():
                report_df, report_headers = create_report(df, estaciones_df, productos_df, empresa_df, month, year, estacion_id, product_id)
                print(report_df)
                if report_df is not None:
                    if '0001' in product_id:
                        header_format = diesel_header_format
                    elif '0002' in product_id:
                        header_format = magna_header_format
                    elif '0003' in product_id:
                        header_format = premium_header_format
                    else:
                        header_format = header_format   
                    
                    for col_num, value in enumerate(report_df.columns.values):
                        worksheet.write(current_row + len(report_headers) , col_num, value, header_format)
                    # Write the report headers
                    for header_row, header in enumerate(report_headers):
                        worksheet.merge_range(current_row + header_row, 0, current_row + header_row, len(report_df.columns) - 1, header, header_format)
                    
                    # Write the report data
                    for row_num, row_data in enumerate(report_df.values):
                        for col_num, cell_value in enumerate(row_data):
                            cell_format = custom_num_format if col_num > 0 else body_format
                            
                            # Check if the cell value is NaN or INF
                            if pd.isna(cell_value) or cell_value in [np.inf, -np.inf]:
                                cell_value = ''  # Replace with empty string or a custom placeholder
                            
                            worksheet.write(current_row + len(report_headers) + 1 + row_num, col_num, cell_value, cell_format)

                        # Set column width
                        for col_num, column in enumerate(report_df.columns):
                            max_len = max(report_df[column].astype(str).apply(len).max(),  # len of largest item
                                        len(str(column)))  # len of column name/header
                            worksheet.set_column(col_num, col_num, max_len + 2)  # add a little extra space
                                        # Update current row for the next report
                    current_row += len(report_headers) + len(report_df) + 3  # +40 for separation
                else:
                    continue
    output.seek(0)
    return output

