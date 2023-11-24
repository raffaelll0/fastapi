import altair as alt
import pandas as pd
import os
from monday_data_extraction import monday
from monday_data_extraction.monday import get_first_and_last_day_of_current_month, get_items

apiKey = monday.apiKey
apiUrl = monday.apiUrl
headers = monday.headers

#QUESTE FUNZIONI SI BASANO DI ESTRARRE DATI DA MONDAY E DI CREARE 1 AD 1 I SINGOLI GRAFICI
# PER POI INSERIRLI NEL PDF GEN

def n_progetti_in_progress_su_pm():

  #make the query
  items = get_items(board_ids=[2286362570],
                    #query_params_str='{rules: [{column_id: "date4", compare_value: ["2023-01-01", "2023-12-31"], operator: between}]}',
                    column_values_ids=["person", "specchio_1"],
                    group_ids=["group_title"],
                    #limit=5
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

  # Split the values in the 'specchio_1' column by commas and convert them to a list
  df['specchio_1'] = df['specchio_1'].apply(lambda x: list(set(x.split(', '))))

  # Convert the lists back to strings
  df['specchio_1'] = df['specchio_1'].apply(lambda x: ', '.join(x))

  #treat person column (sometimes there are 2 people on the same pj)
  df = df.assign(person=df['person'].str.split(', ')).explode('person')
  # Remove leading/trailing whitespace and remove duplicates
  df['person'] = df['person'].str.strip()
  df = df.drop_duplicates().reset_index(drop=True)

  # Group by 'person' and 'specchio_1' and count occurrences
  counts = df.groupby(['person', 'specchio_1']).size().reset_index(name='count')

      # Create an Altair chart
  chart = alt.Chart(counts).mark_bar().encode(
      x=alt.X('person',
              title='PM/SO',
              sort=alt.EncodingSortField(field='count', op='sum')),
      y=alt.Y('count:Q', title='Conteggio'),
      color=alt.Color('specchio_1:N', title='BU'),
      tooltip=['person', 'count', 'specchio_1']
      ).interactive().properties(width=600, height=200)



  chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_1.png")


  chart.save(chart_path)

  return chart_path





def importo_progetti_progress_anno():
    # make the query
    items = get_items(board_ids=[2286362570],
                      column_values_ids=["stato6", "dup__of_tipo"],
                      group_ids=["group_title"],
                      # limit = 50
                      )

    # Loop through the data and create a dataframe
    data_list = []
    for item in items:
        id = item['id']
        anno = item['column_values'][0]['text']
        value = item['column_values'][1]['display_value']

        # Split the string by commas, convert to integers, and calculate the sum
        value = sum(map(float, value.split(', ')))

        data_list.append({'id': id, 'anno': anno, 'value': value})

    # Convert data list to Pandas DataFrame
    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)
    df['value'] = pd.to_numeric(df['value'])  # Convert 'value' column to numeric

    # Group by 'anno' and sum 'value'
    grouped_df = df.groupby('anno')['value'].sum().reset_index()

    # Create Altair chart
    chart = alt.Chart(grouped_df).mark_bar(size=40).encode(
        x='anno:N',
        y='sum(value):Q',
        tooltip=['anno:N', 'sum(value):Q']
    ).properties(width=600, height=200)

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_2.png")

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
    chart = alt.Chart(counts).mark_bar(color='purple').encode(
        x=alt.X('utente',
                title='Assenza (Professionisti)',
                sort=alt.EncodingSortField(field='valore')),
        y=alt.Y('valore:Q', title='Giornate Lavorative'),
        tooltip=['utente', 'valore']
    ).interactive().properties(width=600, height=200)

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

        data_list.append({'id': id, 'tipo': tipo, 'utente': utente, 'valore': valore})

    df = pd.DataFrame(data_list)
    df = df.drop_duplicates().reset_index(drop=True)

    filtered_df = df[df['tipo'] == 'Permesso/ROL']

    # Group by 'utente' and sum 'valore'
    counts = filtered_df.groupby(['utente']).agg({'valore': 'sum'}).reset_index()

    # Create an Altair chart
    chart = alt.Chart(counts).mark_bar(color='red').encode(
        x=alt.X('utente',
                title='Assenza (Professionisti)',
                sort=alt.EncodingSortField(field='valore')),
        y=alt.Y('valore:Q', title='Giornate Lavorative'),
        tooltip=['utente', 'valore']
    ).interactive().properties(width=600, height=200)

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_5.png")

    chart.save(chart_path)

    return chart_path


def analisi_assenze_liberi_professionisti():
    first_day, last_day = get_first_and_last_day_of_current_month()

    # make the query
    items = get_items(board_ids=[3561399641],
                      query_params_str='{rules: [{column_id: "date4", compare_value: ["' + first_day + '", "' + last_day + '"], operator: between}]}',
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
                sort=alt.EncodingSortField(field='valore')),
        y=alt.Y('valore:Q', title='Giornate Lavorative'),
        tooltip=['utente', 'valore']
    ).interactive().properties(width=600, height=200)

    chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_6.png")

    chart.save(chart_path)

    return chart_path


def giornate_smart_working():
  first_day, last_day = get_first_and_last_day_of_current_month()

  #make the query
  items = get_items(board_ids=[3561399641],
                  query_params_str='{rules: [{column_id: "date4", compare_value: ["'+first_day+'", "'+last_day+'"], operator: between}]}',
                  column_values_ids=["status","testo"],
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
  chart = alt.Chart(counts).mark_bar(color='orange').encode(
  x=alt.X('nome_lavoratore',
          title='Nome Lavoratore',
          sort=alt.EncodingSortField(field='count')),
  y=alt.Y('count:Q', title='Giorni di Smart Working'),
  tooltip=['nome_lavoratore','count']
  ).interactive().properties(width=600, height=200)

  chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_7.png")

  chart.save(chart_path)

  return chart_path


def timesheet_mese():

  first_day, last_day = get_first_and_last_day_of_current_month()

  #make the query
  items = get_items(board_ids=[3811872676],
                  query_params_str='{rules: [{column_id: "date", compare_value: ["'+first_day+'", "'+last_day+'"], operator: between}]}',
                  column_values_ids=["text","numeric", "tipo9"],
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
  result_df = df.groupby(['nome_lavoratore','bu'])['ore_rendicontate'].sum().reset_index()

  # Create an Altair chart
  chart = alt.Chart(result_df).mark_bar().encode(
      x=alt.X('nome_lavoratore',
              title='Nome Lavoratore',
              sort=alt.EncodingSortField(field='ore_rendicontate', op='sum')),
      y=alt.Y('ore_rendicontate:Q', title='Ore Rendicontate'),
      color=alt.Color('bu:N', title='BU'),
      tooltip=['nome_lavoratore','ore_rendicontate', 'bu']
      ).interactive().properties(width=600, height=200)

  chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_8.png")

  chart.save(chart_path)

  return chart_path


def bu_h_pie():

  first_day, last_day = get_first_and_last_day_of_current_month()

  #make the query
  items = get_items(board_ids=[3811872676],
                  query_params_str='{rules: [{column_id: "date", compare_value: ["'+first_day+'", "'+last_day+'"], operator: between}]}',
                  column_values_ids=["numeric", "tipo9"],
                  group_ids=["topics"],
                  #limit=50
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

  #plot chart

  chart = alt.Chart(result_df).mark_arc().encode(
    theta="ore_rendicontate:Q",
    color="bu",
    tooltip=["bu", "ore_rendicontate"]
  ).properties(width=600, height=200)
  chart_path = os.path.join(os.path.dirname(__file__), "pngs_of_charts", "chart_9.png")

  chart.save(chart_path)

  return chart_path
