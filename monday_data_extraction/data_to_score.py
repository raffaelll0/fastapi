import requests

from monday_data_extraction import monday
import pandas as pd
from monday_data_extraction.monday import first_and_last_day_of_year, get_first_and_last_day_of_current_month
import json

apiKey = monday.apiKey
apiUrl = monday.apiUrl
headers = monday.headers

get_items = monday.get_items

#QUESTE FUNZIONI SERVONO AD ESTRARRE I DATI NUMERICI DEI PREVENTIVI


def n_tot_prev_accettati_anno():

    # make the queries
    items = get_items(board_ids=[2286362496],
                      column_values_ids=["anno"],
                      group_ids=["nuovo_gruppo10114", "nuovo_gruppo89357"],

                      )

    data_list = []
    for item in items:
        id = item['id']
        if item['column_values'][0]['text'] == '2023':
            anno = item['column_values'][0]['text']
            data_list.append({'id': id, 'anno': anno})

    df = pd.DataFrame(data_list)

    count = len(df)

    return count


def n_tot_prev_accettati_mese():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the queries
    items = get_items(board_ids=[2286362496],
                      query_params_str='{rules: [{column_id: "data", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["anno"],
                      group_ids=["nuovo_gruppo10114", "nuovo_gruppo89357"],

                      )

    data_list = []
    for item in items:
        id = item['id']
        if item['column_values'][0]['text'] == '2023':
            anno = item['column_values'][0]['text']
            data_list.append({'id': id, 'anno': anno})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    count = len(df)

    return count


def n_tot_prev_evasi_mese():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the queries
    items = get_items(board_ids=[2286362496],
                      query_params_str='{rules: [{column_id: "dup__of_data_offerta_contabilt_", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["anno"]

                      )

    data_list = []
    for item in items:
        id = item['id']
        if item['column_values'][0]['text'] == '2023':
            anno = item['column_values'][0]['text']
            data_list.append({'id': id, 'anno': anno})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    count = len(df)

    return count


def prev_acc_consuntivo():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[2286362496],
                      query_params_str='{rules: [{column_id: "data", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["anno"],
                      group_ids=["nuovo_gruppo89357"],
                      # limit=5
                      )

    data_list = []
    for item in items:
        id = item['id']
        anno = item['column_values'][0]['text']

        data_list.append({'id': id, 'anno': anno})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    count = len(df)

    return count


def importo_tot_prev_evasi():
    first_day, last_day = get_first_and_last_day_of_current_month()

    total_sum = 0

    # make the queries
    items = get_items(board_ids=[2286362496],
                      query_params_str='{rules: [{column_id: "dup__of_data_offerta_contabilt_", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["anno", "_importo_offerta_"],
                      group_ids=["topics"]

                      )

    data_list = []
    for item in items:
        id = item['id']
        if item['column_values'][0]['text'] == '2023':
            value = item['column_values'][1].get('value')

            try:
                if value:
                    value = value.strip('"')  # Remove double quotes
            except (ValueError, TypeError):
                print("Warning: Could not convert '{0}' to float. Skipping this value.".format(value))

            data_list.append({'id': id, 'value': value})

    df = pd.DataFrame(data_list)
    # Convert the 'value' column to numeric, ignoring errors
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Remove duplicates based on the 'id' column
    df = df.drop_duplicates(subset='id', keep='first')

    # Calculate the sum of the 'value' column
    total_sum = df['value'].sum()
    total_sum = '{:,.2f}'.format(float(total_sum)).replace(',', ' ').replace('.', ',').replace(' ', '.')

    return total_sum


def importo_tot_prev_accettati():
    total_sum = 0

    # make the queries
    items = get_items(board_ids=[2286362496],
                      column_values_ids=["anno", "dup__of_importo_offerta"],
                      group_ids=["nuovo_gruppo10114", "nuovo_gruppo89357"]
                      )

    data_list = []
    for item in items:
        id = item['id']
        if item['column_values'][0]['text'] == '2023':
            value = item['column_values'][1].get('value')

            try:
                if value:
                    value = value.strip('"')  # Remove double quotes
            except (ValueError, TypeError):
                print("Warning: Could not convert '{0}' to float. Skipping this value.".format(value))

            data_list.append({'id': id, 'value': value})


    df = pd.DataFrame(data_list)

    # Remove duplicates based on the 'id' column
    df = df.drop_duplicates(subset='id', keep='first')

    # Convert the 'value' column to numeric, ignoring errors
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Calculate the sum of the 'value' column
    total_sum = df['value'].sum()
    total_sum = '{:,.2f}'.format(float(total_sum)).replace(',', ' ').replace('.', ',').replace(' ', '.')

    return total_sum


def fatturato_prev_2023():

    first_day, last_day = first_and_last_day_of_year()
    total_sum = 0  # Initialize a variable to store the total sum

    # make the queries
    date4_items = get_items(board_ids=[2430432761],
                            query_params_str='{rules: [{column_id: "date4", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                            column_values_ids=["numeri"]
                            )

    dup__of_data_prevista_items = get_items(board_ids=[2430432761],
                                            query_params_str='{rules: [{column_id: "dup__of_data_prevista", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                                            column_values_ids=["numeri"]
                                            )

    # Merge the two lists based on 'id'
    merged_json = {item['id']: item for item in date4_items + dup__of_data_prevista_items}.values()

    # calculate the total sum
    for item in merged_json:
        numeri_value = item['column_values'][0].get('value')  # Assuming 'value' is the key for the numeri field
        try:
            if numeri_value:
                numeri_value = numeri_value.strip('"')  # Remove double quotes
                total_sum += float(numeri_value)
        except (ValueError, TypeError):
            print("Warning: Could not convert '{0}' to float. Skipping this value.".format(numeri_value))

    rounded_total_sum = round(total_sum, 2)
    rounded_total_sum = '{:,.2f}'.format(float(total_sum)).replace(',', ' ').replace('.', ',').replace(' ', '.')



    return rounded_total_sum


def fatturato_ad_oggi():
    total_sum = 0  # Initialize a variable to store the total sum

    first_day, last_day = first_and_last_day_of_year()

    # make the queries
    date4_items = get_items(board_ids=[2430432761],
                            query_params_str='{rules: [{column_id: "date4", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                            column_values_ids=["numeri"],
                            group_ids=["group_title"]

                            )

    dup__of_data_prevista_items = get_items(board_ids=[2430432761],
                                            query_params_str='{rules: [{column_id: "dup__of_data_prevista", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                                            column_values_ids=["numeri"],
                                            group_ids=["group_title"]
                                            )

    # Merge the two lists based on 'id'
    merged_json = {item['id']: item for item in date4_items + dup__of_data_prevista_items}.values()

    # calculate the total sum
    for item in merged_json:
        numeri_value = item['column_values'][0].get('value')  # Assuming 'value' is the key for the numeri field
        try:
            if numeri_value:
                numeri_value = numeri_value.strip('"')  # Remove double quotes
                total_sum += float(numeri_value)
        except (ValueError, TypeError):
            print("Warning: Could not convert '{0}' to float. Skipping this value.".format(numeri_value))

    rounded_total_sum = round(total_sum, 2)
    rounded_total_sum = '{:,.2f}'.format(float(total_sum)).replace(',', ' ').replace('.', ',').replace(' ', '.')
    return rounded_total_sum


def fatturato_da_emettere():
    total_sum = 0

    # make the queries
    items = get_items(board_ids=[2430432761],
                      column_values_ids=["numeri"],
                      group_ids=["topics", "nuovo_gruppo", "nuovo_gruppo74022", "duplicate_of_0__fatture_in_def"]
                      )

    data_list = []
    for item in items:
        id = item['id']
        if item['column_values'][0].get('value'):
            value = item['column_values'][0].get('value')

            try:
                if value:
                    value = value.strip('"')  # Remove double quotes
            except (ValueError, TypeError):
                print("Warning: Could not convert '{0}' to float. Skipping this value.".format(value))

            data_list.append({'id': id, 'value': value})

    df = pd.DataFrame(data_list)

    # Remove duplicates based on the 'id' column
    df = df.drop_duplicates(subset='id', keep='first')

    # Convert the 'value' column to numeric, ignoring errors
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Calculate the sum of the 'value' column
    total_sum = df['value'].sum()
    total_sum = '{:,.2f}'.format(float(total_sum)).replace(',', ' ').replace('.', ',').replace(' ', '.')


    return total_sum

########################################################################################################################

# REPORT PM NEL DETTAGLIO


def contratto_e_n_progetto(name):
    # make the query

    items = get_items(board_ids=[2286362570],
                      column_values_ids=["file", "numeri0", "person", "link_to_1__hf____offerte"],
                      group_ids=["group_title"]
                      )

    # Initialize variables before the loop
    data_list = []

    # Loop through the data and create a dataframe
    for item in items:
        id = item['id']
        file_count = item['column_values'][0]['value']
        numero_progetto = item['column_values'][1]['text']
        person = item['column_values'][2]['text']
        odv_string = item['column_values'][3]['value']
        odv_data = json.loads(odv_string)

        try:
            odv_linked_pulse_ids = [item['linkedPulseId'] for item in odv_data['linkedPulseIds']]
            odv_linked_pulse_ids = odv_linked_pulse_ids[0]
        except:
            odv_linked_pulse_ids = ""

        if file_count is None:
            file_count = "NO"
        else:
            file_count = "SI"

        if numero_progetto is None:
            numero_progetto = 'Assente'

        data_list.append({'id_progetto': id, 'person': person, 'file': file_count, 'numero progetto': numero_progetto,
                          "odv_linked_pulse_ids": odv_linked_pulse_ids})
    df_progetto = pd.DataFrame(data_list)

    if name != "":
        df_progetto = df_progetto[df_progetto['person'] == name]

    return df_progetto


def n_gu_mese():

    first_day, last_day = get_first_and_last_day_of_current_month()

    #make the query
    items = get_items(board_ids=[3811872676],
                  column_values_ids=["date", "numeric", "board_relation"],
                  query_params_str='{rules: [{column_id: "date", compare_value: ["'+first_day+'", "'+last_day+'"], operator: between}]}', # TODO inserire le date di questo mese
                  group_ids=["topics"],
                  #limit = 500
                  )

    # Initialize variables before the loop
    data_list = []

    # Loop through the data and create a dataframe
    for item in items:

      id_rapportino = item['id']
      date = item['column_values'][0]['text']
      ore_rendicontate = item['column_values'][1]['text']
      ore_rendicontate = float(ore_rendicontate)
      ore_rendicontate = round(ore_rendicontate, 2)
      pj_string = item['column_values'][2]['value']
      pj_data = json.loads(pj_string)

      try:
        pj_linked_pulse_ids = [item['linkedPulseId'] for item in pj_data['linkedPulseIds']]
        pj_linked_pulse_ids = pj_linked_pulse_ids[0]
      except:
        pj_linked_pulse_ids = ""






      data_list.append({'id_rapportino': id_rapportino, 'date': date, 'ore_rendicontate': ore_rendicontate, "pj_linked_pulse_id": pj_linked_pulse_ids})


    df_rapportino = pd.DataFrame(data_list)
    # Group by 'pj_linked_pulse_id' and sum 'ore_rendicontate'
    df_rapportino = df_rapportino.groupby('pj_linked_pulse_id')['ore_rendicontate'].sum().reset_index()

    return df_rapportino


def imponibile():
    #make the query
    items = get_items(board_ids=[2286362496],
                  column_values_ids=["collega_schede19", "dup__of_importo_offerta", "collega_schede2"],
                  group_ids=["nuovo_gruppo10114"],
                  #limit = 30
                  )


      # Initialize variables before the loop
    data_list = []
    count = 0
    # Loop through the data and create a dataframe
    for item in items:
      id_odv = item['id']
      imponibile = item['column_values'][0]['text']
      pj_string = item['column_values'][1]['value']
      id_fattura = item['column_values'][2]['value']

      if imponibile:
        imponibile = float(imponibile)

      else:
        imponibile = 0

      #TODO: rivedere perché non funziona
      try:
        pj_data = json.loads(pj_string)
        pj_linked_pulse_ids = [item['linkedPulseId'] for item in pj_data['linkedPulseIds']]
        pj_linked_pulse_ids = str(pj_linked_pulse_ids[0])
      except:
        pj_linked_pulse_ids = ""

      try:
        fattura_data = json.loads(id_fattura)
        fattura_linked_pulse_ids = [item['linkedPulseId'] for item in fattura_data['linkedPulseIds']]
        fattura_linked_pulse_ids = str(fattura_linked_pulse_ids[0])
      except:
        fattura_linked_pulse_ids = ""






      data_list.append({'id_odv': id_odv, 'imponibile': imponibile,  "pj_linked_pulse_id": pj_linked_pulse_ids, "fattura_linked_pulse_ids": fattura_linked_pulse_ids})


    df_odv = pd.DataFrame(data_list)

    return df_odv


def fatturato_data_chiusura():

    #make the query
    items = get_items(board_ids=[2430432761],
                  column_values_ids=["dup__of_imponibile9", "link_to_1__hf____preventivi", "date4"],
                  #limit = 300
                  )

    # Initialize variables before the loop
    data_list = []

    # Loop through the data and create a dataframe
    for item in items:
      id_fattura = item['id']
      date = item['column_values'][0]['text']
      odv_string = item['column_values'][1]['value']
      fatturato = item['column_values'][2]['text']
      if fatturato:
        fatturato = float(fatturato)

      else:
        fatturato = 0


      try:
        odv_data = json.loads(odv_string)
        odv_linked_pulse_ids = [item['linkedPulseId'] for item in odv_data['linkedPulseIds']]
        odv_linked_pulse_ids = odv_linked_pulse_ids[0]
      except:
        odv_linked_pulse_ids = ""




      data_list.append({'id_fattura': id_fattura, 'fatturato': fatturato,  "odv_linked_pulse_id": odv_linked_pulse_ids, "data_chiusura":date})

    df_fattura = pd.DataFrame(data_list)
    # Convert 'data_chiusura' to datetime type
    df_fattura['data_chiusura'] = pd.to_datetime(df_fattura['data_chiusura'])

    # Group by 'odv_linked_pulse_id', sum 'fatturato', and keep the last 'data_chiusura'
    df_fattura = df_fattura.groupby('odv_linked_pulse_id').agg({'fatturato': 'sum', 'data_chiusura': 'max'}).reset_index()

    # Print the result DataFrame

    return df_fattura


def first_merge():
    df_odv = imponibile()
    df_fattura = fatturato_data_chiusura()


    # Convert 'id_odv' and 'odv_linked_pulse_id' to string before merging if they are not already
    df_odv['id_odv'] = df_odv['id_odv'].astype(str)
    df_fattura['odv_linked_pulse_id'] = df_fattura['odv_linked_pulse_id'].astype(str)

    # Merge dataframes based on the specified condition
    merged_df = pd.merge(df_odv, df_fattura, left_on='id_odv', right_on='odv_linked_pulse_id', how='left')

    # Create 'da_fatturare' column
    merged_df['da_fatturare'] = merged_df['imponibile'] - merged_df['fatturato']

    # if the value is nan, replace with 0
    merged_df['da_fatturare'].fillna(0, inplace=True)
    merged_df['fatturato'].fillna(0, inplace=True)

    # Format columns 'imponibile', 'fatturato', and 'da_fatturare'
    format_currency = lambda x: '{:,.2f}'.format(float(x)).replace(',', ' ').replace('.', ',').replace(' ', '.')
    merged_df['imponibile'] = merged_df['imponibile'].apply(format_currency)
    merged_df['fatturato'] = merged_df['fatturato'].apply(format_currency)
    merged_df['da_fatturare'] = merged_df['da_fatturare'].apply(format_currency)

    # Select specific columns
    result_df = merged_df[['id_odv', 'imponibile', 'pj_linked_pulse_id', 'fatturato', 'data_chiusura', 'da_fatturare']]

    return result_df


def final_merge(name):

    df_rapportino = n_gu_mese()
    df_progetto = contratto_e_n_progetto(name)
    result_df = first_merge()

    # Convert 'pj_linked_pulse_id' and 'id_progetto' to the same data type (e.g., str) before merging
    df_rapportino['pj_linked_pulse_id'] = df_rapportino['pj_linked_pulse_id'].astype(str)
    df_progetto['id_progetto'] = df_progetto['id_progetto'].astype(str)

    # Merge dataframes based on the specified condition
    merged_df = pd.merge(df_rapportino, df_progetto, left_on='pj_linked_pulse_id', right_on='id_progetto', how='left')
    # Merge dataframes based on the specified condition
    merged_df = pd.merge(df_rapportino, df_progetto, left_on='pj_linked_pulse_id', right_on='id_progetto', how='inner')


    merged_df = merged_df[['id_progetto', 'ore_rendicontate', 'file', 'numero progetto', 'odv_linked_pulse_ids']]

    # Convert columns to the same data type
    merged_df['id_progetto'] = merged_df['id_progetto'].astype(str)
    merged_df['odv_linked_pulse_ids'] = merged_df['odv_linked_pulse_ids'].astype(str)

    # Merge dataframes based on the specified conditions
    merged_result = pd.merge(
      merged_df,
      result_df,
      left_on=['id_progetto', 'odv_linked_pulse_ids'],
      right_on=['pj_linked_pulse_id', 'id_odv'],
      how='inner'
    )

    merged_result = merged_result.sort_values(by='ore_rendicontate', ascending=False)
    # Reset the index to start from 0 and drop the existing index
    merged_result = merged_result.reset_index(drop=True)
    merged_result = merged_result.reset_index()

    return merged_result


