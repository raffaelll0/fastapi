import requests
import monday
import altair as alt
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet


from data_to_chart import importo_progetti_progress_anno


apiKey = monday.apiKey
apiUrl = monday.apiUrl
headers = monday.headers

#QUESTE FUNZIONI SI BASANO DI ESTRARRE DATI DA MONDAY E DI CREARE 1 AD 1 I SINGOLI GRAFICI
# PER POI INSERIRLI NEL PDF GEN

def m_progetti_in_progress_su_pm():

    """
    questa funzione prenderà i dati da monday.com, essi verranno
    poi utilizzati per creare dei grafici tramite altair e la libreria pandas
    i grafici di questa funzione si troveranno nella seconda pagina del pdf

    Args:

    Returns:

    """
    query = 'query getItems{ boards (ids:[2286362570]) { items_page(limit:5 ){ cursor items{ id name column_values (ids:["person" "specchio_1"] ) { id text ... on MirrorValue { display_value } } } } } }'
    data = {'query': query}

    # FACCIAMO UNA RICHIESTA JSON
    r = requests.post(url=apiUrl, json=data, headers=headers)

    # DEFINIAMO IL NOSTRO JSON CON LA VARIABILE response_data
    response_data = r.json()

    #print(response_data)

    data = response_data['data']['boards'][0]['items_page']['items']

    # Create a list of dictionaries to store the data
    data_list = []

    # Loop through the data and count occurrences of 'person' and 'specchio_1'
    for item in data:
        person = item['column_values'][1]['text']
        specchio_1 = item['column_values'][0]['display_value']
        data_list.append({'person': person, 'specchio_1': specchio_1})

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data_list)



    df = df.assign(specchio_1=df['specchio_1'].str.split(', ')).explode('specchio_1')
    # Remove leading/trailing whitespace and remove duplicates
    df['specchio_1'] = df['specchio_1'].str.strip()
    df = df.drop_duplicates().reset_index(drop=True)

    df = df.assign(person=df['person'].str.split(', ')).explode('person')
    # Remove leading/trailing whitespace and remove duplicates
    df['person'] = df['person'].str.strip()
    df = df.drop_duplicates().reset_index(drop=True)

    # Group by 'person' and 'specchio_1' and count occurrences
    result_df = df.groupby(['person', 'specchio_1']).size().reset_index(name='count')

    #display(result_df)

    # Create an Altair chart
    chart = alt.Chart(result_df).mark_bar().encode(
        x=alt.X('person', title='PM/SO'),
        y=alt.Y('count:Q', title='Conteggio'),
        color=alt.Color('specchio_1:N', title='BU')
    ).properties(
    width=400,  # Set your custom width
    height=250  # Set your custom height
    )


    chart_path = 'pngs_of_charts/chart.png'

    chart.save(chart_path)
    return chart_path




from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image as ReportlabImage, Spacer
from PIL import Image



def pdf_title_func(title:str, story):
    # CREO UN TITOLO PER LA NUOVA PAGINA
    title = title
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    story.append(title_paragraph)


def create_pdf( pdf_filename):
    """
    Create a one-page PDF with an Altair chart.

    Args:
        chart_path (str): Path to the saved Altair chart PNG.
        pdf_filename (str): Output PDF file name.

    Returns:
        None
    """
    # Create a PDF file with the Altair chart
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Create a list to store the elements for the PDF
    story = []



    # Add the Altair chart image to the story
    img = ReportlabImage('pngs_of_charts/chart.png')
    story.append(img)



    story.append(Spacer(20, 1))

    # Add the Altair chart image to the story
    img_2 = ReportlabImage('pngs_of_charts/chart_2.png')
    story.append(img_2)
    pdf_title_func("hello", story)
    # Add a spacer for better layout
    story.append(Spacer(1, 12))

    # Create a table with two columns
    data = [[ReportlabImage('pngs_of_charts/chart.png'), ReportlabImage('pngs_of_charts/chart_2.png')]]
    table = Table(data, colWidths=[pdf.width / 2] * 4)

    # Apply style to the table
    table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))

    # Add the table to the story
    story.append(table)

    # Build the PDF file with the content in the 'story' list
    pdf.build(story)

# Call the function with the path to the saved Altair chart PNG
#chart_path = m_progetti_in_progress_su_pm()
#chart_path_2 = importo_progetti_progress_anno()


pdf_filename = 'output.pdf'
create_pdf( pdf_filename)






