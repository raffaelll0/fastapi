import requests

from monday_data_extraction import monday
import pandas as pd
from monday_data_extraction.monday import first_and_last_day_of_year, get_first_and_last_day_of_current_month

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
    df = df.drop_duplicates().reset_index(drop=True)

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
    total_sum = '{:,.0f}'.format(float(total_sum))

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
    total_sum = '{:,.0f}'.format(float(total_sum))
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
    rounded_total_sum = '{:,.0f}'.format(float(total_sum))



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
    rounded_total_sum = '{:,.0f}'.format(float(total_sum))
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
    total_sum = '{:,.0f}'.format(float(total_sum))


    return total_sum



