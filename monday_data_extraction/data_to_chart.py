import altair as alt
import pandas as pd
import os
import requests
from monday_data_extraction import monday
from monday_data_extraction.monday import get_first_and_last_day_of_current_month, get_items

apiKey = monday.apiKey
apiUrl = monday.apiUrl
headers = monday.headers

# Define lighter colors for each 'bu' value
bu_colors = {
    'Assenza': 'red',  # red
    'CONS-IMM': '#b2df8a',  # light green
    'CONS-IMP': '#fdbf6f',  # light orange
    'COSTI': '#ff9896',    # light red
    'FM0': 'orange',      # light gray
    'GC-EDI': '#1f78b4',    # darker blue
    'GC-IMP': '#33a02c',
    'GC-IMP, FM0': 'purple',
    'FM0, GC-IMP':'purple',# purple# purple
    'SERV-GEN': 'blue'   # darker pink
}


# QUESTE FUNZIONI SI BASANO DI ESTRARRE DATI DA MONDAY E DI CREARE 1 AD 1 I SINGOLI GRAFICI
# PER POI INSERIRLI NEL PDF GEN

def n_progetti_in_progress_su_pm(person_name, path_str):
    # make the query
    items = get_items(board_ids=[2286362570],
                      # query_params_str='{rules: [{column_id: "date4", compare_value: ["2023-01-01", "2023-12-31"], operator: between}]}',
                      column_values_ids=["person", "specchio_1"],
                      group_ids=["group_title"],
                      # limit=5
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        person = item['column_values'][1]['text']
        specchio_1 = item['column_values'][0]['display_value']
        data_list.append({'id': id, 'person': person, 'specchio_1': specchio_1})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    # Split the values in 'specchio_1' and explode the resulting lists
    df['specchio_1'] = df['specchio_1'].str.split(', ')
    df = df.explode('specchio_1')
    # Group by 'person' and 'specchio_1', then count the occurrences
    df = df.groupby(['person', 'specchio_1']).size().reset_index(name='count')

    # Additional aggregation to get the total sum for each person
    total_counts = df.groupby('person')['count'].sum().reset_index(name='total_count')

    # Merge the total_counts with counts on 'person' column
    counts = pd.merge(df, total_counts, on='person', how='left')

    if person_name != "":
        counts = counts[counts['person'] == person_name]
        condition = False

    else:
        condition = True

    # Calculate the new maximum value by adding 500,000
    max_value = counts['total_count'].max() + 20

    # Create an Altair chart
    chart = alt.Chart(counts).mark_bar().encode(
        x=alt.X('person:N',
                title='PM/SO',
                sort=alt.EncodingSortField(field='count', op='sum', order='ascending'),
                axis=alt.Axis(labelAngle=45, labelFontSize=16, labels=condition), ),
        y=alt.Y('count:Q', title='', scale=alt.Scale(domain=[0, max_value])),
        color=alt.Color('specchio_1:N', title='BU',
                        scale=alt.Scale(domain=list(bu_colors.keys()), range=list(bu_colors.values()))),
        tooltip=['person', 'count', 'specchio_1']
    ).interactive().properties(width=600, height=200,
                               title=alt.TitleParams(text='N Progetti in Progress su PM', fontSize=20))

    # Create text labels for the summed count values
    text = alt.Chart(counts).mark_text(dx=0, dy=-10, color='black').encode(
        x=alt.X('person:N',
                sort=alt.EncodingSortField(field='count', op='sum', order='ascending')),
        y=alt.Y('total_count:Q'),
        text=alt.Text('total_count:Q', format='.0f'),
        tooltip=['person', 'total_count']
    )

    # Combine the bar chart and text labels
    chart = chart + text




    if path_str == "":
        path_str = "chart_1.png"

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", path_str)

    chart.save(chart_path)

    return chart_path


def importi_progress_pm(person_name, path_str):
    # make the query
    items = get_items(board_ids=[2286362570],
                      column_values_ids=["person", "dup__of_tipo", "dup__of_residuo"],
                      group_ids=["group_title"],
                      # limit=100
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        name = item['column_values'][0]['text']
        accettato = item['column_values'][1]['display_value']
        contabilizzato = item['column_values'][2]['display_value']

        if name != "":

            # Check if the value is not an empty string before converting to float
            if accettato and accettato.strip():
                # Split the string by commas, convert to float, and calculate the sum
                sum_accettati = sum(map(float, accettato.split(', ')))

                if contabilizzato and contabilizzato.strip():
                    sum_contabilizzato = sum(map(float, contabilizzato.split(', ')))

                    # Calculate the difference between sum_accettati and sum_contabilizzato
                    residuo = sum_accettati - sum_contabilizzato
                else:
                    sum_contabilizzato = 0
                    residuo = sum_accettati - sum_contabilizzato

                # Append the data to the list including the residuo
                data_list.append({'id': id, 'name': name, 'accettati': sum_accettati, 'residuo': residuo})
        else:
            pass

    # Create a Pandas DataFrame
    df = pd.DataFrame(data_list)
    # Drop duplicates after splitting
    df.drop_duplicates(subset=['id', 'name'], inplace=True)
    # treat person column (sometimes there are 2 people on the same pj)
    df = df.assign(name=df['name'].str.split(', ')).explode('name')

    if person_name != "":
        df = df[df['name'] == person_name]
        df = df.groupby('name').agg({'accettati': 'sum', 'residuo': 'sum'}).reset_index()
        header = alt.Header(titleFontSize=24, labelExpr="''")

    else:
        df = df.groupby('name').agg({'accettati': 'sum', 'residuo': 'sum'}).reset_index()
        header = alt.Header(titleFontSize=20)
    # Melt the DataFrame to have a 'variable' column for 'accettati' and 'residuo'
    df_melted = pd.melt(df, id_vars=['name'], value_vars=['accettati', 'residuo'],
                        var_name='variable', value_name='value')

    base = alt.Chart(df_melted, width=alt.Step(55)).encode(
        alt.X("variable:N", title="", axis=alt.Axis(labels=False)),
        alt.Y("sum(value):Q", title=""),
        alt.Color("variable:N", title="Legenda"),
        alt.Text("sum(value):Q", format=",.2f"),
    )

    chart = alt.layer(
        base.mark_bar(),
        base.mark_text(dy=-10)
    ).facet(
        alt.Column("name:N", title='Importi Progetti in Progress per PM',
                   header=header,
                   sort=alt.EncodingSortField(field="value", op="sum", order="ascending"), ),

    ).configure_facet(spacing=0)

    if path_str == "":
        path_str = "chart_10.png"

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", path_str)

    chart.save(chart_path)

    return chart_path



def importo_progress_bu(name, path_str):
    # make the query
    items = get_items(board_ids=[2286362570],
                      column_values_ids=["specchio_1", "dup__of_tipo", "person"],
                      group_ids=["group_title"],
                      # limit = 1
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        tag = item['column_values'][0]['display_value']
        person = item['column_values'][1]['text']
        value = item['column_values'][2]['display_value']

        if tag != "":
            # Check if the value is not an empty string before converting to float
            if value and value.strip():  # Check if the value is not empty or just whitespace
                # Split the string by commas, convert to integers, and calculate the sum
                values = sum(map(float, value.split(', ')))
                data_list.append({'id': id, 'sum_values': values, 'tag': tag, 'person': person})

    # Create a Pandas DataFrame
    df = pd.DataFrame(data_list)
    df.drop_duplicates(subset=['id', 'tag'], inplace=True)
    df = df.assign(tag=df['tag'].str.split(', ')).explode('tag')
    if name != "":
        df.drop_duplicates(subset=['id', 'tag', 'person'], inplace=True)
        # Group by 'person' and 'tag', and sum the 'sum_values'
        df_grouped = df.groupby(['person', 'tag'])['sum_values'].sum().reset_index()
        # filter by the name
        df_grouped = df_grouped[df_grouped['person'] == name]

    else:
        df_grouped = df.groupby('tag', as_index=False)['sum_values'].sum()

    # Create an Altair chart
    chart = alt.Chart(df_grouped).mark_bar().encode(
        x=alt.X('tag:N', sort=alt.EncodingSortField(field='sum_values', op='sum', order='ascending'),
                axis=alt.Axis(title='', labelAngle=0, labelFontSize=14)),
        y=alt.Y('sum(sum_values):Q', axis=alt.Axis(title='')),
        tooltip=['tag:N', 'sum(sum_values):Q']
    ).properties(
        width=600,
        height=400,
        title=alt.TitleParams(text='Importi progetti in Progress per BU', fontSize=24)
    )

    # Create text labels for the summed values
    text = alt.Chart(df_grouped).mark_text(dx=0, dy=-10, color='black').encode(
        x=alt.X('tag:N', sort=alt.EncodingSortField(field='sum_values', op='sum', order='ascending'),
                axis=alt.Axis(title='')),
        y=alt.Y('sum(sum_values):Q'),
        text=alt.Text('sum(sum_values):Q', format=',.2f'),
        tooltip=['tag:N', 'sum(sum_values):Q']
    ).interactive().properties(
        width=600,
        height=400
    )

    # Combine the bar chart and text labels
    chart = chart + text

    if path_str == "":
        path_str = "chart_11.png"

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", path_str)

    chart.save(chart_path)

    return chart_path


def importo_progetti_progress_anno(name, path_str):
    # make the query
    items = get_items(board_ids=[2286362570],
                      column_values_ids=["stato6", "dup__of_tipo", "person"],
                      group_ids=["group_title"],
                      # limit = 50
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        anno = item['column_values'][0]['text']
        person = item['column_values'][1]['text']
        value = item['column_values'][2]['display_value']

        if value:
            # Split the string by commas, convert to integers, and calculate the sum
            value = sum(map(float, value.split(', ')))

        data_list.append({'id': id, 'anno': anno, 'value': value, 'person': person})

    # Convert data list to Pandas DataFrame
    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)
    df['value'] = pd.to_numeric(df['value'])

    if name != "":
        # Group by 'anno' and sum 'value'
        grouped_df = df.groupby(['person', 'anno'])['value'].sum().reset_index()
        grouped_df = grouped_df[grouped_df['person'] == name]

    else:
        # Group by 'anno' and sum 'value'
        grouped_df = df.groupby('anno')['value'].sum().reset_index()

    # Create Altair chart
    chart = alt.Chart(grouped_df).mark_bar(size=80).encode(

        x=alt.X('anno:N', axis=alt.Axis(title='', labelAngle=0, labelFontSize=14)),
        y='sum(value):Q',
        tooltip=['anno:N', 'sum(value):Q']
    ).properties(width=400)

    # Create text labels for the summed values
    text = alt.Chart(grouped_df).mark_text(dx=0, dy=-10, color='black').encode(
        x=alt.X('anno:N', title=''),
        y=alt.Y('sum(value):Q', axis=alt.Axis(title='')),
        text=alt.Text('sum(value):Q', format=',.2f'),
        tooltip=['anno:N', 'sum(value):Q']
    ).interactive().properties(width=400,
                               title=alt.TitleParams(text='Importi progetti in Progress per anno', fontSize=20))

    # Combine the bar chart and text labels
    chart = chart + text

    if path_str == "":
        path_str = "chart_2.png"

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", path_str)

    chart.save(chart_path)

    return chart_path


def portafoglio_ordine_residuo():
    # make the query
    items = get_items(board_ids=[2286362570],
                      column_values_ids=["dup__of_tipo"],
                      group_ids=["group_title"],
                      # limit = 50
                      )

    global group_title

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        values_str = item['column_values'][0]['display_value']

        # Split the string by commas, convert to integers, and calculate the sum
        values = sum(map(float, values_str.split(', ')))

        data_list.append({'id': id, 'sum_values': values})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    # Calculate the sum of 'sum_values'
    total_sum = df['sum_values'].sum()

    # Create a DataFrame with the total sum
    total_df = pd.DataFrame({'Total Sum': [total_sum]})

    # Create an Altair chart
    chart = alt.Chart(total_df).mark_bar(size=40).encode(
        y=alt.Y('Total Sum:Q', title='Summed Values'),

        tooltip=['Total Sum']

    ).interactive().properties(width=600, height=200, title="in progress")

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_3.png")

    chart.save(chart_path)

    return chart_path


def analisi_ferie_malattia():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[3561399641],
                      query_params_str='{rules: [{column_id: "date4", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["status", "numeri0", "testo"],
                      group_ids=["group_title"],
                      # limit = 50
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        utente = item['column_values'][0]['text']
        tipo = item['column_values'][1]['text']
        valore = item['column_values'][2]['text']
        valore = float(valore) / 8

        data_list.append({'id': id, 'tipo': tipo, 'utente': utente, 'valore': valore})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    filtered_df = df[~df['tipo'].isin(['Permesso/ROL', 'Assenza (Professionisti)', 'Smart Working'])]

    # Group by 'utente' and sum 'valore'
    counts = filtered_df.groupby(['utente']).agg({'valore': 'sum'}).reset_index()

    # Create an Altair chart
    chart = alt.Chart(counts).mark_bar(color='green').encode(
        x=alt.X('utente',
                title='',
                sort=alt.EncodingSortField(field='valore'),
                axis=alt.Axis(labelAngle=45, labelFontSize=18)),
        y=alt.Y('valore:Q', title='Giornate Lavorative'),
        tooltip=['utente', 'valore']
    ).interactive().properties(width=600, height=200, title=alt.TitleParams(text='Analisi Ferie - Malattia - Dayhospital - Dipendenti', fontSize=20))

    # Create text labels for the summed values
    text = alt.Chart(counts).mark_text(dx=0, dy=50, color='black').encode(
        x=alt.X('utente', sort=alt.EncodingSortField(field='valore')),
        y=alt.Y('valore:Q'),
        text=alt.Text('valore:Q', format='.2f'),
        tooltip=['utente', 'valore']
    ).interactive()

    # Combine the bar chart and text labels
    chart = chart + text

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_4.png")

    chart.save(chart_path)

    return chart_path


def analisi_permessi_rol():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[3561399641],
                      query_params_str='{rules: [{column_id: "date4", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["status", "numeri0", "testo"],
                      # limit = 50
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        utente = item['column_values'][0]['text']
        tipo = item['column_values'][1]['text']
        valore = item['column_values'][2]['text']

        if valore:
            valore = float(valore)
        else:
            valore = 0.0

        data_list.append({'id': id, 'tipo': tipo, 'utente': utente, 'valore': valore})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    filtered_df = df[df['tipo'] == 'Permesso/ROL']

    # Group by 'utente' and sum 'valore'
    counts = filtered_df.groupby(['utente']).agg({'valore': 'sum'}).reset_index()

    # Create an Altair chart
    chart = alt.Chart(counts).mark_bar(color='orange').encode(
        x=alt.X('utente',
                title='',
                sort=alt.EncodingSortField(field='valore'),
                axis=alt.Axis(labelAngle=0, labelFontSize=18)),
        y=alt.Y('valore:Q', title='Giornate Lavorative'),
        tooltip=['utente', 'valore']
    ).interactive().properties(width=600, height=200, title=alt.TitleParams(text='Analisi Permessi/ROL Dipendenti', fontSize=20))

    # Create text labels for the summed values
    text = alt.Chart(counts).mark_text(dx=0, dy=10, color='black').encode(
        x=alt.X('utente',
                title='',
                sort=alt.EncodingSortField(field='valore')),
        y=alt.Y('valore:Q'),
        text=alt.Text('valore:Q'),
        tooltip=['utente', 'valore']
    ).interactive()

    # Combine the bar chart and text labels
    chart = chart + text


    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_5.png")

    chart.save(chart_path)

    return chart_path


def analisi_assenze_liberi_professionisti():
    first_day, last_day = get_first_and_last_day_of_current_month()


    #TODO update the values of first and last day

    # make the query
    items = get_items(board_ids=[3561399641],
                      query_params_str='{rules: [{column_id: "date4", compare_value: ["2023-11-01", "2023-11-30"], operator: between}]}',
                      column_values_ids=["status", "numeric", "testo"],
                      # limit = 50
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        utente = item['column_values'][0]['text']
        tipo = item['column_values'][1]['text']
        valore = item['column_values'][2]['text']

        valore = float(valore)

        data_list.append({'id': id, 'tipo': tipo, 'utente': utente, 'valore': valore})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    filtered_df = df[df['tipo'] == 'Assenza (Professionisti)']

    # Group by 'utente' and sum 'valore'
    counts = filtered_df.groupby(['utente']).agg({'valore': 'sum'}).reset_index()

    # Create an Altair chart
    chart = alt.Chart(counts).mark_bar().encode(
        x=alt.X('utente',
                title='Assenza (Professionisti)',
                sort=alt.EncodingSortField(field='valore'),
                axis=alt.Axis(labelAngle=0, labelFontSize=18)),
        y=alt.Y('valore:Q', title='Giornate Lavorative'),
        tooltip=['utente', 'valore']
    ).interactive().properties(width=600, height=200, title=alt.TitleParams(text='Analisi Assenze Liberi Professionisti', fontSize=20))

    # Create text labels for the summed values
    text = alt.Chart(counts).mark_text(dx=0, dy=25, color='black').encode(
        x=alt.X('utente',
                title='Assenza (Professionisti)',
                sort=alt.EncodingSortField(field='valore')),
        y=alt.Y('valore:Q'),
        text=alt.Text('valore:Q', format='.2f'),
        tooltip=['utente', 'valore']
    ).interactive()

    # Combine the bar chart and text labels
    chart = chart + text

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_6.png")

    chart.save(chart_path)

    return chart_path


def giornate_smart_working():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[3561399641],
                      query_params_str='{rules: [{column_id: "date4", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["status", "testo"],
                      limit=50
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        nome_lavoratore = item['column_values'][0]['text']
        tipo = item['column_values'][1]['text']
        data_list.append({'id': id, 'nome_lavoratore': nome_lavoratore, 'tipo': tipo})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    filtered_df = df[df['tipo'] == 'Smart Working']

    # Group by 'person' and 'specchio_1' and count occurrences
    counts = filtered_df.groupby(['nome_lavoratore']).size().reset_index(name='count')

    # Create an Altair chart
    chart = alt.Chart(counts).mark_bar(color='blue').encode(
        x=alt.X('nome_lavoratore',
                title=' ',
                sort=alt.EncodingSortField(field='count'),
                axis=alt.Axis(labelAngle=0, labelFontSize=18)),
        y=alt.Y('count:Q', title='Giorni di Smart Working'),
        tooltip=['nome_lavoratore', 'count']
    ).interactive().properties(width=600, height=200, title=alt.TitleParams(text='Analisi giornate Smart Working', fontSize=20))

    text = alt.Chart(counts).mark_text(dx=0, dy=15, color='black').encode(
        x=alt.X('nome_lavoratore',
                title='',
                sort=alt.EncodingSortField(field='count')),
        y=alt.Y('count:Q'),
        text=alt.Text('count:Q'),
        tooltip=['nome_lavoratore', 'count']
    ).interactive()

    # Combine the bar chart and text labels
    chart = chart + text

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_7.png")

    chart.save(chart_path)

    return chart_path


def timesheet_mese():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[3811872676],
                      query_params_str='{rules: [{column_id: "date", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["text", "numeric", "tipo9"],
                      group_ids=["topics"]
                      )
    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        nome_lavoratore = item['column_values'][0]['text']
        ore_rendicontate = item['column_values'][1]['text']
        bu = item['column_values'][2]['text']
        data_list.append({'id': id, 'nome_lavoratore': nome_lavoratore, 'ore_rendicontate': ore_rendicontate, 'bu': bu})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    # Parse "ore_rendicontate" to float
    df['ore_rendicontate'] = df['ore_rendicontate'].astype(float)

    # Group by "bu" and sum "ore_rendicontate"
    result_df = df.groupby(['nome_lavoratore', 'bu'])['ore_rendicontate'].sum().reset_index()

    # Create a new column representing the sum of 'residuo' and 'sum_accettati'
    result_df['total'] = result_df.groupby('nome_lavoratore')['ore_rendicontate'].transform('sum')

    # Calculate the new maximum value by adding 500,000
    max_value = result_df['total'].max() + 20


    # Create an Altair chart
    chart = alt.Chart(result_df).mark_bar().encode(
        x=alt.X('nome_lavoratore',
                title='',
                sort=alt.EncodingSortField(field='ore_rendicontate', op='sum'),
                axis=alt.Axis(labelAngle=45, labelFontSize=16)),
        y=alt.Y('ore_rendicontate:Q', title='Ore Rendicontate', scale=alt.Scale(domain=[0, max_value])),
        color=alt.Color('bu:N', title='BU'),
        tooltip=['nome_lavoratore', 'ore_rendicontate', 'bu']
    ).interactive().properties(width=600, height=200, title=alt.TitleParams(text='Timesheet Mese', fontSize=20))

    # Create text labels for the summed values
    text = alt.Chart(result_df).mark_text(dx=0, dy=-10, color='black').encode(
        x=alt.X('nome_lavoratore', sort=alt.EncodingSortField(field='ore_rendicontate', op='sum', order='ascending')),
        y=alt.Y('sum(ore_rendicontate):Q'),
        text=alt.Text('sum(ore_rendicontate):Q', format='.2f'),
        tooltip=['nome_lavoratore:N', 'sum(ore_rendicontate):Q']
    ).interactive()

    # Combine the bar chart and text labels
    chart = chart + text

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_8.png")

    chart.save(chart_path)

    return chart_path


def bu_h_pie():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[3811872676],
                      query_params_str='{rules: [{column_id: "date", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
                      column_values_ids=["numeric", "tipo9"],
                      group_ids=["topics"],
                      # limit=50
                      )
    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        ore_rendicontate = item['column_values'][0]['text']
        bu = item['column_values'][1]['text']
        data_list.append({'id': id, 'ore_rendicontate': ore_rendicontate, 'bu': bu})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    # Parse "ore_rendicontate" to float
    df['ore_rendicontate'] = df['ore_rendicontate'].astype(float)

    # Group by "bu" and sum "ore_rendicontate"
    result_df = df.groupby('bu')['ore_rendicontate'].sum().reset_index()

    # Add a new column 'color' based on the 'bu' values
    result_df['color'] = result_df['bu'].map(bu_colors)

    # Calculate the total sum of ore_rendicontate for each tag
    total_by_bu = result_df['ore_rendicontate'].sum()

    # Add a new column 'ore_rendicontate_percentage' representing the percentage
    result_df['ore_rendicontate_percentage'] = (result_df['ore_rendicontate'] / total_by_bu) * 100
    # Round the percentage values to a specified number of decimal places
    result_df['ore_rendicontate_percentage'] = result_df['ore_rendicontate_percentage'].round(2).astype(str)
    result_df['ore_rendicontate_percentage'] = result_df['ore_rendicontate_percentage'] + "%"

    # plot chart

    chart = alt.Chart(result_df).mark_arc().encode(
        theta=alt.Theta("ore_rendicontate:Q", stack=True),
        color="bu",
        tooltip=["bu", "ore_rendicontate"]
    ).mark_arc(outerRadius=120).properties(width=350, height=350, title=alt.TitleParams(text='BU/h', fontSize=20))

    text = chart.mark_text(radius=150, size=14).encode(text="ore_rendicontate_percentage:N")
    chart = chart + text



    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_9.png")

    chart.save(chart_path)

    return chart_path


##################################

def resoconto_budget_consuntivo_player():
    query = '{boards(ids: 2787765150){ groups(ids:"topics") { items_page(limit:200){items{ column_values(ids: ["dup__of_pm8"]) { ... on MirrorValue { display_value } } subitems{ id column_values(ids:["monitoraggio_tempo5" "numeri" "status" "person"]){ value id text type } } } } }} }'
    data = {'query': query}

    # Make a request to the GraphQL endpoint
    r = requests.post(url=apiUrl, json=data, headers=headers)
    response_data = r.json()

    items = response_data['data']['boards'][0]['groups'][0]['items_page']['items']

    # Loop through the data and create a dataframe
    count = 0
    data_list = []
    for item in items:
        tipo = item['column_values'][0]['display_value']
        if "CONS" in tipo:
            # stato = item['column_values'][0]['display_value']
            for sub_item in item['subitems']:
                count = count + 1
                id = sub_item['id']
                name = sub_item['column_values'][0]['text']
                time_1 = sub_item['column_values'][1]['text']
                time_2 = sub_item['column_values'][3]['value']
                stato = sub_item['column_values'][2]['text']

                if name:
                    # check if time is none
                    if time_1 == "":
                        time_1 = 0
                    # else it returns only the number of hours (no minutes)
                    else:
                        # Split the string into hours and minutes
                        hours, minutes, seconds = map(int, time_1.split(':'))

                        # Calculate the total hours
                        time_1 = hours + minutes / 60 + seconds / 3600

                    if time_2 is None:
                        time_2 = 0

                    else:
                        time_2 = float(time_2.replace('"', ''))

                    diff = time_2 - (time_1 / 8)
                    # Append the data to the list including the residuo
                    data_list.append({'id': id, 'name': name, 'diff': diff, 'stato': stato})
                else:
                    pass
        else:
            pass

    # Create a Pandas DataFrame
    df = pd.DataFrame(data_list)
    # Drop duplicates after splitting
    df.drop_duplicates(subset=['id', 'name'], inplace=True)
    # treat person column (sometimes there are 2 people on the same pj)
    df = df.assign(name=df['name'].str.split(', ')).explode('name')
    # Group by 'name' and sum the values
    df = df.groupby(['name', 'stato']).agg({'diff': 'sum'}).reset_index()
    # Filter out rows with empty names after grouping
    df = df[df['name'] != '']

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('name', title='', sort='y', axis=alt.Axis(labelAngle=45, labelFontSize=18)),

        y=alt.Y('sum(diff)', title='GU'),
        color='stato',
        tooltip=['name', 'stato', 'diff']
    ).interactive().properties(width=600, height=200, title=alt.TitleParams(text='Differenza tra Budget e Consuntivo Per Player', fontSize=20))

    # Create text labels for the summed values
    text = alt.Chart(df).mark_text(dx=0, dy=-20, color='black').encode(
        x=alt.X('name', sort='y'),
        y=alt.Y('sum(diff):Q'),
        text=alt.Text('sum(diff):Q', format='.2f'),
        tooltip=['name:N', 'sum(diff):Q']
    ).interactive().properties(width=600, height=200)

    # Combine the bar chart and text labels
    chart = chart + text

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_12.png")

    chart.save(chart_path)

    return chart_path

def fatturazione_in_progress_media(name, path_str):
  #make the query
  items = get_items(board_ids=[2286362570],
                  column_values_ids=["dup__of_residuo", "dup__of_tipo", "person"],
                  group_ids=["group_title"],
                  limit = 200
                  )

  # Initialize variables before the loop
  data_list = []

  # Loop through the data and create a dataframe
  for item in items:
      id = item['id']
      person = item['column_values'][0]['text']
      accettato = item['column_values'][1]['display_value']
      contabilizzato = item['column_values'][2]['display_value']

      # Initialize percentuale
      percentuale = 0
      if ',' in accettato:
          accettato = None
      else:
        if accettato != '' and accettato != '0':
          if contabilizzato == '' or contabilizzato == '0':
            percentuale = 0
            data_list.append({'id': id, 'percentuale': percentuale, 'person': person})
          else:
            # Split the string by commas, convert to floats, and calculate the sum
            contabilizzato = sum(map(float, contabilizzato.split(', ')))

            # Split the string by commas, convert to floats, and calculate the sum
            accettato = sum(map(float, accettato.split(', ')))
            percentuale = ( contabilizzato / accettato) * 100
            percentuale = round(percentuale, 1)
            data_list.append({'id': id, 'percentuale': percentuale, 'person': person})


        else:
          data_list.append({'id': id, 'percentuale': percentuale, 'person': person})

  # Convert data list to Pandas DataFrame
  df = pd.DataFrame(data_list)
  # Drop duplicates after splitting
  df.drop_duplicates(subset=['id'], inplace=True)
  # Filter the DataFrame for rows where 'person' is "Chiara Bernacchi"
  df = df[df['person'] == name]
  # Calculate the average of 'percentuale' for each person
  df = df.groupby('person')['percentuale'].mean().reset_index()

  # Calculate the average of 'percentuale' for each person
  avg_df = df.groupby('person')['percentuale'].mean().reset_index()

  # Create an Altair chart
  chart = alt.Chart(avg_df).mark_bar().encode(
      x=alt.X('person:N', title='', axis=alt.Axis(labelAngle=0, labelFontSize=18, labels=False)),
      y=alt.Y('mean(percentuale):Q', title='%'),
      tooltip=['person:N', 'mean(percentuale):Q']
  ).properties(width=400, title=alt.TitleParams(text='Fatturazione Progetti In Progress (Media)', fontSize=20))

  if path_str == "":
      path_str = "chart_13.png"

  chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", path_str)

  chart.save(chart_path)

  return chart_path

def numero_progetti_in_progress_anno(name):

    #make the query
    items = get_items(board_ids=[2286362570],
                  column_values_ids=["stato6", "person"],
                  group_ids=["group_title"],
                  #limit = 50
                  )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
      id = item['id']
      anno = item['column_values'][0]['text']
      person = item['column_values'][1]['text']

      data_list.append({'id': id, 'anno': anno, 'person': person})

    # Convert data list to Pandas DataFrame
    df = pd.DataFrame(data_list)

    # Filter the DataFrame for rows where 'person' is "Chiara Bernacchi"
    df = df[df['person'] == name]
    df = df.drop_duplicates().reset_index(drop=True)
    # Group by 'anno' and count occurrences
    df = df.groupby('anno').size().reset_index(name='count')

    # Create Altair chart
    chart = alt.Chart(df).mark_bar(size=80).encode(
      x=alt.X('anno:N',axis=alt.Axis(title='', labelAngle=0, labelFontSize=16)),
      y=alt.Y('count:Q', title=''),
      tooltip=['anno:N', 'count:Q']
    ).properties(width=400, title=alt.TitleParams(text='Numero Progetti in progress Per Anno', fontSize=20))

    # Create text labels for the counts
    text = alt.Chart(df).mark_text(dx=0, dy=10, color='black').encode(
      x='anno:N',
      y='count:Q',
      text=alt.Text('count:Q', format='.0f'),
      tooltip=['anno:N', 'count:Q']
    ).interactive().properties(width=400)

    # Combine the bar chart and text labels

    chart = chart + text

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_13.png")

    chart.save(chart_path)

    return chart_path

# Example usage with the name "Chiara Bernacchi"
#n_progetti_in_progress_su_pm('Chiara Bernacchi', 'chart_chiara.png')
#importi_progress_pm("Chiara Bernacchi", "importi_progress_pm_chiara.png")
#fatturazione_in_progress_media('Chiara Bernacchi', 'fatturazione_in_progress_media_chiara.png')

# Example usage with dynamic tags
#importo_progress_bu(["FM0","CONS-IMP", "CONS-IMM"], "importo_progress_bu.png")

#numero_progetti_in_progress_anno()

# Example usage with dynamic years
#importo_progetti_progress_anno(["2020", "2021", "2022", "2023"], "importo_progetti_progress_anno_filtered.png")

