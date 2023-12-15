import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, white
import os
from io import BytesIO
import pandas as pd


import monday_data_extraction.data_to_score
from monday_data_extraction import data_to_chart
from monday_data_extraction import data_to_score
from monday import today, mese_corrente, anno_corrente


def header(pdf):
    # HEADER
    # Get the dimensions of the img
    x_offset = 600
    y_offset = 820

    # Add an image at the top as a header
    logo_width = 110  # Adjust the width of the image as needed
    logo_height = 100  # Adjust the height of the image as needed
    # Use os.path.join to construct the absolute path
    header_path = os.path.join(os.path.dirname(__file__), "imgs", "logo_accaeffe.jpg")

    pdf.drawInlineImage(header_path, x=x_offset - logo_width / 1, y=y_offset - logo_height - 20, width=logo_width,
                        height=logo_height)

    # HEADER


def footer(pdf):
    # FOOTER
    # Get the dimensions of the img
    x_offset = 550
    y_offset = 130

    # Add an image at the top as a header
    logo_width = 480  # Adjust the width of the image as needed
    logo_height = 100  # Adjust the height of the image as needed

    footer_path = os.path.join(os.path.dirname(__file__), "imgs", "footer_HF.png")

    pdf.drawInlineImage(footer_path, x=x_offset - logo_width / 1, y=y_offset - logo_height - 20, width=logo_width,
                        height=logo_height)

    # FOOTER


def num_pag(pdf, n):
    # Add text to the bottom right corner
    page_number_text = f"     {n}"
    page_width, page_height = letter
    pdf.setFont("Helvetica", 12)  # Set font to bold and size 16
    pdf.drawString(page_width - pdf.stringWidth(page_number_text, 'Helvetica', 12) - 20, 20, page_number_text)


def title(pdf, text, y_offset):
    # TITLE
    # Add bold title in the center
    pdf.setFont("Helvetica-Bold", 16)  # Set font to bold and size 16



    # Calculate the position for the center of the page
    x_position = (pdf._pagesize[0] - pdf.stringWidth(text, "Helvetica-Bold", 16)) / 2
    y_position = y_offset

    pdf.drawString(x_position, y_position, text)
    # TITLE


def descriptions(pdf, text_1, text2, x_offset, y_offset):

    # DESCRIPTIONS
    # Add description lines
    pdf.setFont("Helvetica", 12)  # Set font to regular and size 12
    pdf.drawString(x_offset, y_offset, text_1)
    pdf.drawString(x_offset, y_offset - 20, text2)
    # DESCRIPTIONS


def draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset):
    total_width = num_boxes * (box_width + 10)
    starting_x_offset = (pdf._pagesize[0] - total_width) / 2

    for i in range(num_boxes):
        current_x_offset = starting_x_offset + i * (box_width + 10)
        underline_y_offset = current_y_offset + 62


        pdf.rect(current_x_offset, current_y_offset, box_width, box_height, stroke=1, fill=0)

        # Add the title above the number
        title_text = box_titles[i]
        title_x_position = current_x_offset + box_width / 2
        title_y_position = current_y_offset + box_height - 15

        pdf.setFont("Times-Bold", 8)  # Set initial font size
        font_size = 8  # Initial font size
        while pdf.stringWidth(title_text, "Times-Bold", font_size) > box_width - 3 and font_size > 5:
            font_size -= 1
        pdf.setFont("Times-Bold", font_size)
        pdf.drawCentredString(title_x_position, title_y_position, title_text)

        # Add underline under the title
        underline_length = box_width
        pdf.line(current_x_offset + (box_width - underline_length) / 2, underline_y_offset,
                 current_x_offset + (box_width + underline_length) / 2, underline_y_offset)

        # Add the number inside the box
        value_text = box_values[i]
        value_x_position = current_x_offset + box_width / 2
        value_y_position = current_y_offset + box_height / 3

        pdf.setFont("Helvetica-Bold", 22)
        font_size = 22  # Reset font size for number
        while pdf.stringWidth(value_text, "Helvetica-Bold", font_size) > box_width - 10 and font_size > 5:
            font_size -= 1
        pdf.setFont("Helvetica-Bold", font_size)
        pdf.drawCentredString(value_x_position, value_y_position, value_text)


def draw_chart_under_description(pdf, chart_path, x_offset, y_offset, logo_width, logo_height):
    if x_offset is None:
        # Calculate the position for the center of the page
        x_offset = (pdf._pagesize[0] - logo_width) / 2

    pdf.drawInlineImage(chart_path, x=x_offset, y=y_offset - logo_height - 20, width=logo_width,
                        height=logo_height)


def box_titles(pdf, x_offset, y_offset, text_1):
    # Add description lines
    pdf.setFont("Helvetica", 12)  # Set font to regular and size 12
    #pdf.drawString(x_offset, y_offset, text_1)
    # Split the text into lines based on the newline character
    lines = text_1.split('\n')

    # Draw each line separately
    for line in lines:
        pdf.drawString(x_offset, y_offset, line)
        y_offset -= 10  # Adjust the line spacing as needed


def box_descriptions(pdf, x_offset, y_offset, num_sets, box_details_list):
    for i in range(num_sets):
        n_boxes = 8  # Adjust the number of boxes as needed
        box_details = box_details_list[i] if i < len(box_details_list) else [""] * n_boxes
        create_boxes(pdf, n_boxes, box_details, x_offset=x_offset, y_offset=y_offset, desc_height=10, custom_height=25)
        y_offset -= 25


def create_boxes(pdf, n_boxes, box_details, x_offset, y_offset, desc_height, custom_height=None):
    box_width = 85  # Default width for most columns
    indice_column_width = 30  # Adjust the width for the "Indice" column
    space_between_boxes = 0  # Adjust the space between boxes as needed

    # Define custom widths for "N Progetto", "Contratto SI/NO", and "GU lavorate nel mese" boxes
    n_progetto_width = 50
    contratto_width = 60
    gu_lavorate_width = 75

    # Calculate the total horizontal space needed for all boxes
    total_width = (
        n_progetto_width + contratto_width + gu_lavorate_width +
        (n_boxes - 3) * (box_width + space_between_boxes)
    )

    # Calculate the starting x position for the first box
    x_position = (pdf._pagesize[0] - total_width) / 2 + x_offset

    for i in range(n_boxes):
        # Check if the current box is for the "Indice" column
        if i == 0:
            current_box_width = indice_column_width
        elif i == 1:  # Adjust the condition for "N Progetto" column
            current_box_width = n_progetto_width
        elif i == 2:  # Adjust the condition for "Contratto SI/NO" column
            current_box_width = contratto_width
        elif i == 7:  # Adjust the condition for "GU lavorate nel mese" column
            current_box_width = gu_lavorate_width
        else:
            current_box_width = box_width

        # Draw the box
        pdf.setStrokeColor(black)
        pdf.setFillColor(white)
        box_height = custom_height if custom_height is not None else 60
        pdf.rect(x_position, y_offset, current_box_width, box_height, fill=True)

        # Set fill color to black for text
        pdf.setFillColor(black)

        # Add description lines under the box
        box_titles(pdf, x_position, y_offset + desc_height, box_details[i])

        # Update the x position for the next box
        x_position += current_box_width + space_between_boxes


list_pm = ["Chiara Bernacchi", "Angelo Ducoli", "Christian Trocino", "Edgardo Maffezzoli", "Giovanni Erbicella",
           "Luca Capozzi", "Nicolo Balsamo", "Raffaele Tardi"]


def indice_conteggi(pdf):
    # INDICE START
    print("Generating indice and conteggi...")
    # HEADER START
    header(pdf)

    # TITLE START
    title(pdf, text=f"REPORT KPI {mese_corrente()}  {anno_corrente()}", y_offset=680)

    # TITLE START
    title(pdf, text="INDICE", y_offset=650)
    n_indice = 6
    empty_string = "                                                                        "

    # DESCRIPTIONS START
    descriptions(pdf, text_1="RESOCONTO PREVENTIVI                          ______________________Pag 1",
                 text2="ANALISI OPERATIVA PROGETTI                 ______________________Pag 2",
                 x_offset=50,
                 y_offset=600)

    # DESCRIPTIONS START

    descriptions(pdf, text_1="CONTROLLO DI GESTIONE                         ______________________Pag 3",
                 text2=f"", x_offset=50,
                 y_offset=560)

    # DESCRIPTIONS START
    y = 540
    for pm in list_pm:
        descriptions(pdf, text_1=f"REPORT PM KPI: {pm}",
                     text2="", x_offset=50,
                     y_offset=y)

        descriptions(pdf, text_1=f"{empty_string}______________________Pag{n_indice}",
                     text2="",
                     x_offset=50,
                     y_offset=y)

        y -= 20
        n_indice += 1

    # DESCRIPTIONS START
    for pm in list_pm:
        descriptions(pdf, text_1=f"REPORT PM Dettaglio: {pm}",
                     text2="", x_offset=50,
                     y_offset=y)

        descriptions(pdf, text_1=f"{empty_string}______________________Pag{n_indice}",
                     text2="",
                     x_offset=50,
                     y_offset=y)
        y -= 20
        n_indice += 1

    # FOOTER START
    footer(pdf)
    num_pag(pdf, "0")

    # INDICE END

    # FIRST PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE START
    title(pdf, text=f"REPORT KPI {mese_corrente()}  {anno_corrente()}", y_offset=680)
    # TITLE END

    # DESCRIPTIONS START
    descriptions(pdf, text_1="Autore del report: Christian Trocino", text2=f"Dati aggiornati al: {today()} ",
                 x_offset=50,
                 y_offset=650)
    # DESCRIPTIONS END

    # TITLE_2 START
    title(pdf, text=f"PERIODO DI RIFERIMENTO: {mese_corrente()}  {anno_corrente()}", y_offset=600)
    # TITLE_2 END

    # BOX_1 START
    # TAKE ALL THE VALUES FROM DATA TO SCORE
    tot_prev_evasi_mese = data_to_score.n_tot_prev_evasi_mese()
    tot_prev_acc_mese = data_to_score.n_tot_prev_accettati_mese()
    tot_prev_acc_cons = data_to_score.prev_acc_consuntivo()
    tot_prev_evasi_tot = data_to_score.importo_tot_prev_evasi()

    num_boxes = 4
    box_titles = ["PREVENTIVI EVASI", "PREVENTIVI ACCETTATI", "PREV. ACCETTATI CONSUNTIVO",
                  "IMPORTO PREV EVASI"]
    box_values = [str(tot_prev_evasi_mese), str(tot_prev_acc_mese), str(tot_prev_acc_cons),
                  str(tot_prev_evasi_tot) + ' €']
    box_width = 120
    box_height = 80

    draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset=480)
    # BOX_1 END

    # TITLE_3 START
    title(pdf, text=f"PERIODO DI RIFERIMENTO: ANNO {anno_corrente()}", y_offset=450)
    # TITLE_3 END

    # BOX_2 START
    # TAKE ALL THE VALUES FROM DATA TO SCORE
    tot_prev_acc = data_to_score.n_tot_prev_accettati_anno()
    tot_prev_acc_importo = data_to_score.importo_tot_prev_accettati()

    num_boxes = 2
    box_titles = ["PREVENTIVI ACCETTATI", "IMPORTO PREV. ACCETTATI"]
    box_values = [str(tot_prev_acc), str(tot_prev_acc_importo) + ' €']
    box_width = 120
    box_height = 80

    draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset=340)
    # BOX_2 END

    # BOX_3 START
    # TAKE ALL THE VALUES FROM DATA TO SCORE
    fatturato_ad_oggi = data_to_score.fatturato_ad_oggi()
    fatturato_da_emettere = data_to_score.fatturato_da_emettere()
    fatturato_previsto = data_to_score.fatturato_prev_2023()

    num_boxes = 3
    box_titles = ["FATTURATO AD OGGI", "FATTURATO DA EMETTERE", f"FATTURATO PREVISTO {anno_corrente()}"]
    box_values = [str(fatturato_ad_oggi) + ' €', str(fatturato_da_emettere) + ' €', str(fatturato_previsto) + ' €']
    box_width = 120
    box_height = 80

    draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset=240)
    # BOX_3 END

    # FOOTER START
    footer(pdf)
    # FOOTER END
    num_pag(pdf, "1")

    print("Done!")


def analisi_operativa_progetti(pdf):
    print("Generating Analisi Operativa Progetti...")
    # SECOND PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE_3 START
    title(pdf, text="ANALISI OPERATIVA PROGETTI", y_offset=710)
    # TITLE_3 END

    # DESCRIPTIONS + IMG START

    # Draw Altair chart image under the description
    chart_path = data_to_chart.n_progetti_in_progress_su_pm("", "")
    #chart_path = r'pngs_of_charts/chart_1.png'
    draw_chart_under_description(pdf, chart_path, x_offset=60, y_offset=720, logo_width=510, logo_height=200)

    chart_path = data_to_chart.importi_progress_pm("", "")
    #chart_path = r'C:\Users\raffaele.loglisci\PycharmProjects\pdf_heroku\monday_data_extraction\pngs_of_charts\chart_10.png'
    draw_chart_under_description(pdf, chart_path, x_offset=50, y_offset=520, logo_width=500, logo_height=200)

    chart_path = data_to_chart.importo_progress_bu("", "")
    #chart_path = r'C:\Users\raffaele.loglisci\PycharmProjects\pdf_heroku\monday_data_extraction\pngs_of_charts\chart_11.png'
    draw_chart_under_description(pdf, chart_path, x_offset=40, y_offset=320, logo_width=475, logo_height=180)

    # DESCRIPTIONS + IMG END

    # FOOTER START
    footer(pdf)
    # FOOTER END
    num_pag(pdf, "2")
    # SECOND PAGE END
    print("Done!")


def controllo_di_gestione(pdf):
    print("Generating Controllo di Gestione...")
    #######################################################################################################################
    # THIRD PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE_4 START
    title(pdf, text="CONTROLLO DI GESTIONE", y_offset=700)
    # TITLE_4 END

    # DESCRIPTIONS + IMG START

    # Draw Altair chart image under the description
    chart_path = data_to_chart.analisi_ferie_malattia()
    # chart_path = r'pngs_of_charts/chart_4.png'
    draw_chart_under_description(pdf, chart_path, x_offset=85, y_offset=700, logo_width=460, logo_height=200)

    chart_path = data_to_chart.analisi_permessi_rol()
    # chart_path = r'pngs_of_charts\chart_5.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=485, logo_width=450, logo_height=170)

    chart_path = data_to_chart.giornate_smart_working()
    # chart_path = r'pngs_of_charts\chart_6.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=300, logo_width=450, logo_height=170)

    # DESCRIPTIONS + IMG END

    # FOOTER START
    footer(pdf)
    # FOOTER END
    # THIRD PAGE END
    num_pag(pdf, "3")
    ########################################################################################################################

    # FOURTH PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE_4 START
    title(pdf, text="CONTROLLO DI GESTIONE", y_offset=700)
    # TITLE_4 END

    # DESCRIPTIONS + IMG START

    # Draw Altair chart image under the description
    chart_path = data_to_chart.analisi_assenze_liberi_professionisti()
    # chart_path = r'pngs_of_charts/chart_7.png'
    draw_chart_under_description(pdf, chart_path, x_offset=75, y_offset=710, logo_width=450, logo_height=180)

    chart_path = data_to_chart.timesheet_mese()
    # chart_path = r'pngs_of_charts\chart_8.png'
    draw_chart_under_description(pdf, chart_path, x_offset=80, y_offset=540, logo_width=450, logo_height=200)

    chart_path = data_to_chart.bu_h_pie()
    # chart_path = r'pngs_of_charts\chart_9.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=330, logo_width=250, logo_height=200)

    # DESCRIPTIONS + IMG END

    # FOOTER START
    footer(pdf)
    # FOOTER END
    # FOURTH PAGE END
    num_pag(pdf, 4)
    #######################################################################################################################
    # FIFTH PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # Draw Altair chart image under the description
    chart_path = data_to_chart.resoconto_budget_consuntivo_player()
    # chart_path = r'pngs_of_charts/chart_7.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=720, logo_width=500, logo_height=300)

    # FOOTER START
    footer(pdf)
    # FOOTER END
    # FIFTH PAGE END
    num_pag(pdf, "5")
    print("Done!")


def report_nel_dettaglio(pdf, shared_data):
    print("Generating Report nel Dettaglio...")

    num = shared_data[0]

    for pm in list_pm:
        print(pm)
        # SIXT PAGE START
        pdf.showPage()
        # HEADER START
        header(pdf)
        # HEADER END


        # TITLE_4 START
        title(pdf, text=f"REPORT PM KPI: {pm}", y_offset=710)
        # TITLE_4 END

        # DESCRIPTIONS + IMG START
        # LEFT
        # descriptions(pdf, text_1="Numero Progetti In Progress", text2="", x_offset=50, y_offset=660)
        # Draw Altair chart image under the description
        chart_path = data_to_chart.n_progetti_in_progress_su_pm(pm, 'chart_chiara.png')
        # chart_path = r'pngs_of_charts/chart_chiara.png'
        draw_chart_under_description(pdf, chart_path, x_offset=20, y_offset=710, logo_width=280, logo_height=180)

        # descriptions(pdf, text_1="Fatturazione Progetti In Progress (Media)", text2="", x_offset=50, y_offset=500)
        chart_path = data_to_chart.fatturazione_in_progress_media(pm, 'fatturazione_in_progress_media_chiara.png')
        # chart_path = r'pngs_of_charts\fatturazione_in_progress_media_chiara.png'
        draw_chart_under_description(pdf, chart_path, x_offset=10, y_offset=525, logo_width=250, logo_height=180)

        # descriptions(pdf, text_1="Numero Progetti in progress Per Anno", text2="", x_offset=50, y_offset=310)
        chart_path = data_to_chart.numero_progetti_in_progress_anno(pm)
        # chart_path = r'pngs_of_charts\importo_progetti_progress_anno_filtered.png'
        draw_chart_under_description(pdf, chart_path, x_offset=15, y_offset=330, logo_width=250, logo_height=180)
        # LEFT

        # RIGHT

        # Draw Altair chart image under the description

        chart_path = data_to_chart.importi_progress_pm(pm, "importi_progress_pm_chiara.png")
        # chart_path = r'pngs_of_charts/importi_progress_pm_chiara.png'
        draw_chart_under_description(pdf, chart_path, x_offset=300, y_offset=710, logo_width=310, logo_height=170)

        chart_path = data_to_chart.importo_progress_bu(pm, "importo_progress_bu.png")
        # chart_path = r'pngs_of_charts\importo_progress_bu.png'
        draw_chart_under_description(pdf, chart_path, x_offset=295, y_offset=530, logo_width=300, logo_height=190)

        chart_path = data_to_chart.importo_progetti_progress_anno(pm, "importo_progetti_progress_anno_filtered.png")
        # chart_path = r'pngs_of_charts\chart_13.png'
        draw_chart_under_description(pdf, chart_path, x_offset=295, y_offset=335, logo_width=300, logo_height=190)

        # RIGHT

        num += 1
        num_pag(pdf, num)
        # DESCRIPTIONS + IMG END

        # FOOTER START
        footer(pdf)
        # FOOTER END
        # SIXTH PAGE END

    shared_data[0] = num
    print("Done!")


def report_pm_kpi(pdf, shared_data):
    print("Generating Report PM KPI...")
    num = shared_data[0]

    # SEVENTH PAGE START

    for pm in list_pm:
        def chunks(lst, chunk_size):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]

        # # Create boxes with descriptions
        box_details = [
            (" N "),
            (" N\n Progetto"),
            (" Contratto\n SI/NO"),
            (" Imponibile "),
            (" Fatturato"),
            (" Da Fatturare"),
            (" Data Prevista\n Chiusura"),
            (" GU lavorate\n nel mese")
        ]
        n_boxes = len(box_details)

        # # Add data from DataFrame to PDF
        merged_result = monday_data_extraction.data_to_score.final_merge(pm)

        # Create multiple sets of boxes with descriptions
        empty = " "
        box_details_list = [
            [' ' + str(row['index']),
             '   ' + str(row['numero progetto']),
             '   ' + str(row['file']),
             ' ' + str(row['imponibile'] + ' €'),
             ' ' + str(row['fatturato'] + ' €'),
             ' ' + str(row['da_fatturare'] + ' €'),  # Round 'Da Fatturare' to 2 decimal places
             ' ' + str(row['data_chiusura'].strftime('%d-%m-%Y') if not pd.isnull(row['data_chiusura']) else ''),
             '   ' + "{:.2f}".format(float(row['ore_rendicontate']))]
            # Format 'Data Chiusura' if not NaT)]  # Format 'Data Chiusura'
            for _, row in merged_result.iterrows()
        ]

        row_counter = 0  # Counter to keep track of the rows processed

        for box_details_set in chunks(box_details_list, 20):  # Process 20 rows at a time
            pdf.showPage()  # Add a new page
            header(pdf)
            title(pdf, text=f"REPORT PM  Dettaglio: {pm}", y_offset=680)
            create_boxes(pdf, n_boxes, box_details, x_offset=20, desc_height=40, y_offset=600)
            box_descriptions(pdf, x_offset=20, y_offset=595, num_sets=len(box_details_set),
                             box_details_list=box_details_set)
            row_counter += len(box_details_set)
            footer(pdf)
            num += 1
            num_pag(pdf, num)

        # FOOTER START
        footer(pdf)
        # FOOTER END
        # SEVENTH PAGE END
    print("Done!")


def retry_function(func, *args, max_attempts=3, delay=1):
    attempts = 0

    while attempts < max_attempts:
        try:
            func(*args)
            break  # If successful, exit the loop
        except Exception as e:
            attempts += 1
            print(f"Error in '{func.__name__}'. Retrying ({attempts}/{max_attempts})...")
            time.sleep(delay)  # Add a delay between retries (optional)

    if attempts == max_attempts:
        raise Exception(f"Maximum attempts reached for '{func.__name__}'. Unable to proceed.")


def create_pdf(file_path):
    # Create a BytesIO buffer to capture the PDF content
    buffer = BytesIO()
    # Create a PDF document
    pdf = canvas.Canvas(file_path, pagesize=letter)

    shared_list = [5]  # Initial value for 'num' in a list

    # Create all the parts of the PDF
    #retry_function(indice_conteggi, pdf)
    #retry_function(analisi_operativa_progetti, pdf)
    retry_function(controllo_di_gestione, pdf)
    # retry_function(report_nel_dettaglio, pdf, shared_list)
    # retry_function(report_pm_kpi, pdf, shared_list)

    # Save the PDF to the specified file path
    pdf.save()

    # Get the content of the buffer (bytes) and return it
    pdf_bytes = buffer.getvalue()

    # Close the buffer to free up resources
    buffer.close()

    return pdf_bytes


# Specify the file path for the PDF
pdf_file_path = "pdf_with_image.pdf"

# Call the function to create the PDF with the image
create_pdf(pdf_file_path)

print(f"PDF with image created successfully at: {pdf_file_path}")