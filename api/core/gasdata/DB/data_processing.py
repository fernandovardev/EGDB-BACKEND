from datetime import datetime
import pandas as pd
from .db_config import special_stations, product_order, data
from .db_config import create_dispen_df, create_stock_df
from datetime import timedelta

def process_and_merge_data(data_dict):
    # Extract the dataframes from the dictionary
    vtasanblas_data = data_dict['vtasanblas_data'].groupby(['FECHA', 'ESTACION', 'PRODUCTO']).sum().reset_index()
    descsanblas_data = data_dict['descsanblas_data'].groupby(['FECHA', 'ESTACION', 'PRODUCTO']).sum().reset_index()
    pruebassanblas_data = data_dict['pruebassanblas_data'].groupby(['FECHA', 'ESTACION', 'PRODUCTO']).sum().reset_index()
    #movmedtanqsanblas_data = data_dict['movmedtanqsanblas_data']
    movdepprin_data = data_dict['movdepprin_data']
    movsuper_data = data_dict['movsuper_data']
    movvtacombust_data = data_dict['movvtacombust_data']
    descargas_data = data_dict['descargas_data']
    pruebas_data = data_dict['pruebas_data']
    movmedtanq_data = data_dict['movmedtanq_data']
    movdepprinsanblas_data = data_dict['movdepprinsanblas_data']
    


########################################################################################################################################################################################################################   
    vtasanblas_data['FECHA'] = pd.to_datetime(vtasanblas_data['FECHA'])
    descsanblas_data['FECHA'] = pd.to_datetime(descsanblas_data['FECHA'])
    pruebassanblas_data['FECHA'] = pd.to_datetime(pruebassanblas_data['FECHA'])
    #movmedtanqsanblas_data['FECHA'] = pd.to_datetime(movmedtanqsanblas_data['FECHA'])

##########################################################################################################################################################################################
    # Grouping and summing the 'movdepprin_data' by 'FECHA' and 'ESTACION'.
    # This operation aggregates all entries per station and date.
    depositos_df = movdepprin_data.groupby(['FECHA', 'ESTACION']).sum().reset_index()

    # Similar operation for 'movsuper_data', aggregating sales data per station and date.
    vtas_super_df = movsuper_data.groupby(['FECHA', 'ESTACION']).sum().reset_index()

    # Merging 'vtas_super_df' with 'depositos_df' on 'ESTACION' and 'FECHA'.
    # The 'outer' join ensures that all dates and stations are included, even if they only appear in one DataFrame.
    # Missing values are filled with 0, which is suitable for financial sums in this context.
    efectivo_df = vtas_super_df.merge(depositos_df, on=['ESTACION', 'FECHA'], how='outer').fillna(0)


    # Renaming columns for clarity: 'IMPVENTA' to 'SUPER' and 'IMPORTE' to 'PANAMERICANO'.
    # These new names are presumably more descriptive of the data they represent.
    efectivo_df = efectivo_df.rename(columns={'IMPVENTA': "SUPER", 'IMPORTE': "PANAMERICANO"})

    # Converting the 'FECHA' column to a datetime format for consistent date handling.
    efectivo_df['FECHA'] = pd.to_datetime(efectivo_df['FECHA'])

    # Combining 'efectivo_df' with 'movdepprinsanblas_data'.
    # This concatenation adds another set of data to the already prepared 'efectivo_df'.
    # It is important that both DataFrames have the same structure and columns for proper concatenation.
    efectivo_df = pd.concat([efectivo_df, movdepprinsanblas_data])
    ######################################################################################################################################################################################################################################################################################################################################
    ######################################################################################################################################################################################################################################################################################################################################
    # Copying the original DataFrame to avoid modifying it directly.
    movvtacombust_df = movvtacombust_data.copy()

    # Truncating 'PRODUCTO' column to the first 4 characters.
    # This might be necessary if 'PRODUCTO' includes additional, non-relevant characters.
    movvtacombust_df['PRODUCTO'] = movvtacombust_df['PRODUCTO'].str[:4]

    # Converting 'FECHA' to datetime for consistency and ease of manipulation.
    movvtacombust_df['FECHA'] = pd.to_datetime(movvtacombust_df['FECHA'])

    # Filtering out special stations for separate processing.
    # 'special_stations' should be a list of station identifiers that require special handling.
    df_special = movvtacombust_df[movvtacombust_df['ESTACION'].isin(special_stations)]

    # Adjusting the 'FECHA' for records with 'TURNO' == '1' to the previous day.
    # This is likely a business rule specific to these stations.
    df_special_shift1_next_day = df_special[df_special['TURNO'] == '1'].assign(FECHA=lambda x: x['FECHA'] - pd.Timedelta(days=1))

    # Combining the adjusted special stations data with other turns from special stations.
    # The data is then grouped and summed by 'FECHA', 'ESTACION', and 'PRODUCTO'.
    df_special_combined = pd.concat([
        df_special[df_special['TURNO'].isin(['2', '3', '4'])],
        df_special_shift1_next_day
    ]).groupby(['FECHA', 'ESTACION', 'PRODUCTO']).sum().reset_index()

    # Processing the remaining stations that are not in the special list.
    df_others = movvtacombust_df[~movvtacombust_df['ESTACION'].isin(special_stations)]
    df_others_sum = df_others.groupby(['FECHA', 'ESTACION', 'PRODUCTO']).sum().reset_index()

    # Combining data from special and other stations, then sorting.
    final_df = pd.concat([df_special_combined, df_others_sum]).sort_values(['FECHA', 'ESTACION', 'PRODUCTO'])

    # Dropping the 'TURNO' column if it exists, as it's no longer needed after processing.
    # 'errors='ignore'' ensures that no error is raised if the column does not exist.
    ventas_df = final_df.drop(columns='TURNO', errors='ignore')

    # Resultant DataFrame 'ventas_df' now holds the processed sales data.
    ventas_df = pd.concat([ventas_df, vtasanblas_data]).sort_values(['FECHA', 'ESTACION', 'PRODUCTO'])
    ########################################################################################################################################################################################################################
    ######################################################################################################################################################################################################################################################################################################################################
    # Process 'compras_df' from 'descargas_data'
    # Truncate the 'PRODUCTO' column to the first 4 characters for standardization
    compras_df = descargas_data.copy()
    compras_df['PRODUCTO'] = compras_df['PRODUCTO'].str[:4]
    compras_df['FECHA'] = pd.to_datetime(compras_df['FECHA'])

    # Grouping and summing 'compras_df' by 'FECHA', 'ESTACION', and 'PRODUCTO'
    # This operation aggregates the purchase data per station, product, and date
    compras_df = compras_df.groupby(['FECHA', 'ESTACION', 'PRODUCTO']).sum().reset_index()
    compras_df = pd.concat([compras_df, descsanblas_data]).sort_values(['FECHA', 'ESTACION', 'PRODUCTO'])

    ######################################################################################################################################################################################################################################################################################################################################
    ######################################################################################################################################################################################################################################################################################################################################
    # Preparing 'pruebas_df' from 'pruebas_data'
    # Extracting 'CODE' from the first 5 characters of 'DESCRIPCION'
    pruebas_df = pruebas_data.copy()
    pruebas_df['CODE'] = pruebas_df['DESCRIPCION'].str[:5]
    pruebas_df['FECHA'] = pd.to_datetime(pruebas_df['FECHA'])

    # Extracting and converting 'VOLUMEN' from 'DESCRIPCION'
    # Assumes that 'VOLUMEN' is embedded within the string at a specific position
    pruebas_df['VOLUMEN'] = pruebas_df['DESCRIPCION'].str[6:13].astype(float)

    # Merging 'pruebas_df' with 'dispen_df' on matching 'CODE' and 'ESTACION'
    # 'left_on' and 'right_on' specify the columns to merge on for each DataFrame
    merged_df = pd.merge(pruebas_df, create_dispen_df(), left_on=['CODE', 'ESTACION'], right_on=['codigo', 'Station_id'], how='left')

    # Renaming columns for clarity
    merged_df = merged_df.rename(columns={'numerotanque': 'TANQUE', 'producto_id': 'PRODUCTO'})

    # Dropping columns no longer needed after the merge
    # Then grouping and summing the data by 'FECHA', 'ESTACION', and 'PRODUCTO'
    summed_pruebas = merged_df.drop(columns=['codigo', 'Station_id', 'DESCRIPCION', 'CODE', 'TANQUE']
                        ).groupby(['FECHA', 'ESTACION', 'PRODUCTO']
                        ).sum().reset_index()
    summed_pruebas = pd.concat([summed_pruebas, pruebassanblas_data]).sort_values(['FECHA', 'ESTACION', 'PRODUCTO'])
    ######################################################################################################################################################################################################################################################################################################################################
    ######################################################################################################################################################################################################################################################################################################################################
    # First, ensure that HORAMOV is a datetime
    #movmedtanqsanblas_data['HORAMOV'] = pd.to_datetime(movmedtanqsanblas_data['HORAMOV'])

    # Then, subtract the date part from the datetime to get the time since midnight as a timedelta
    #movmedtanqsanblas_data['FECHA'] = movmedtanqsanblas_data['FECHA'] - timedelta(days=1)
    movmedtanq_df=movmedtanq_data
    print(movmedtanq_df)
    movmedtanq_df.to_csv('medidas.csv')
    return efectivo_df, compras_df, summed_pruebas, ventas_df, movmedtanq_df


