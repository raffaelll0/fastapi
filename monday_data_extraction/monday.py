import requests
from datetime import datetime
import calendar

from babel.dates import format_date, format_datetime, format_time



apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE0NTc5NTQ4MywiYWFpIjoxMSwidWlkIjoyNzk4NzQzMywiaWFkIjoiMjAyMi0wMi0xNFQwODoyOTo0NC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTExOTUwMTIsInJnbiI6InVzZTEifQ.j052k96lwfIBOtLGWng2xmZul4c_rWnguMOTduJ95DM"
apiUrl = "https://api.monday.com/v2"
headers = {
    'Content-Type': 'application/json',
    'Authorization': apiKey,
    'API-Version': '2023-10'
}


def anno_corrente():
    current_year = datetime.now().year

    return current_year


def mese_corrente():

    # Set the locale to Italian
    locale = 'it_IT'

    # Get the current month in text
    current_month_text = format_date(datetime.now(), format='MMMM', locale=locale)
    return current_month_text


def today():
    # Get today's date
    today_date = datetime.today().date()
    return today_date


def get_first_and_last_day_of_current_month():
    # Get the current date
    current_date = datetime.now()

    # Calculate the first day of the current month
    first_day = current_date.replace(day=1)

    # Calculate the last day of the current month
    _, last_day = calendar.monthrange(current_date.year, current_date.month)
    last_day = current_date.replace(day=last_day)

    # Format dates as "YYYY-MM-DD"
    first_day_str = first_day.strftime("%Y-%m-%d")
    last_day_str = last_day.strftime("%Y-%m-%d")

    return first_day_str, last_day_str


def first_and_last_day_of_year():
    # Get the current date
    current_date = datetime.now()

    # Calculate the first day of the current year
    first_day = current_date.replace(month=1, day=1)

    # Calculate the last day of the current year
    last_day = current_date.replace(month=12, day=31)

    # Format dates as "YYYY-MM-DD"
    first_day_str = first_day.strftime("%Y-%m-%d")
    last_day_str = last_day.strftime("%Y-%m-%d")

    return first_day_str, last_day_str




def get_items(board_ids:list , column_values_ids:list, group_ids:list = None, limit:int = 500, query_params_str:str = None, cursor:str = None):

    all_items = []


    #global group_title

    if group_ids is None:
      my_group_ids_str = ""
      group_ids_str = ""
      group_ids_closing =""

    else:
      my_group_ids_str = "$my_group_ids: [String!]"
      group_ids_str = "{groups(ids:$my_group_ids)"
      group_ids_closing ="title }"

    if  query_params_str is None:
      query_params_str =""
    else:
      query_params_str = f", query_params: {query_params_str}"



    while True:
      if cursor is None:
        cursor_str = ""
      else:
        cursor_str = f', cursor: "{cursor}"'
        #print(cursor_str)
        query_params_str = ""

      # Define the initial query to fetch the first set of data
      query = 'query ($my_board_id: [ID!]!, $my_colummn_values_ids: [String!], $my_limit: Int!'+my_group_ids_str+') { boards(ids:$my_board_id)'+ group_ids_str +' { items_page(limit:$my_limit'+query_params_str + cursor_str +') { cursor items { id name column_values(ids:$my_colummn_values_ids){id text value ... on MirrorValue { display_value }}}} ' + group_ids_closing + ' }}'
      #print(query)
      vars = {
          'my_limit': limit,
          'my_board_id':board_ids,
          'my_query_params': query_params_str,
          'my_colummn_values_ids':column_values_ids,
          'my_group_ids': group_ids
          }

      data = {'query': query, 'variables': vars}

      # Make a request to the GraphQL endpoint
      r = requests.post(url=apiUrl, json=data, headers=headers)
      response_data = r.json()
      #print(response_data)

      if group_ids is None:
        items = response_data['data']['boards'][0]['items_page']['items']
        cursor = response_data['data']['boards'][0]['items_page']['cursor']
        #print(len(items))
        # Append items to the accumulated list
        all_items.extend(items)

      else:
        cursor = response_data['data']['boards'][0]['groups'][0]['items_page']['cursor']

        #if response_data['data']['boards'][0]['groups'][0]['title']:
         # group_title = response_data['data']['boards'][0]['groups'][0]['title']
        #else:
          #group_title = None


        for n, id in enumerate(group_ids):
          items = response_data['data']['boards'][0]['groups'][n]['items_page']['items']
          #all_items.extend(items)
          #print(len(items))
         # Append items to the accumulated list
          all_items.extend(items)


      # Append items to the accumulated list
      #all_items.extend(items)

      if limit != 500:
        break

      if cursor is None:
          break

    return(all_items)
