from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, white
import os
from io import BytesIO

from monday_data_extraction import data_to_chart
from monday_data_extraction import data_to_score
def header(pdf):
    # HEADER
    # Get the dimensions of the img
    x_offset = 550
    y_offset = 800

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

        pdf.setFont("Times-Bold", 12)  # Set initial font size
        font_size = 12  # Initial font size
        while pdf.stringWidth(title_text, "Times-Bold", font_size) > box_width - 10 and font_size > 5:
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

        pdf.setFont("Helvetica-Bold", 24)
        font_size = 24  # Reset font size for number
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


def box_descriptions(pdf, x_offset, y_offset, num_sets):
    for _ in range(num_sets):
        n_boxes = 7  # Adjust the number of boxes as needed
        box_details = [
            ("Box 1"),
            ("Box 2"),
            ("Box 3"),
            ("Box 4"),
            ("Box 5"),
            ("Box 6"),
            ("Box 7")
        ]
        create_boxes(pdf, n_boxes, box_details, x_offset=x_offset, y_offset=y_offset, desc_height=15, custom_height=35)
        y_offset -= 35

def create_boxes(pdf, n_boxes, box_details, x_offset, y_offset, desc_height, custom_height=None):
    box_width = 80  # Adjust the width of the box as needed
    space_between_boxes = 0  # Adjust the space between boxes as needed

    # Calculate the total horizontal space needed for all boxes
    total_width = n_boxes * (box_width + space_between_boxes)

    # Calculate the starting x position for the first box
    x_position = (pdf._pagesize[0] - total_width) / 2 + x_offset

    for i in range(n_boxes):

        # Draw the box
        pdf.setStrokeColor(black)
        pdf.setFillColor(white)
        box_height = custom_height if custom_height is not None else 60  # Adjust the height of the second line
        pdf.rect(x_position, y_offset, box_width, box_height, fill=True)

        # Set fill color to black for text
        pdf.setFillColor(black)

        # Add description lines under the box
        box_titles(pdf, x_position, y_offset + desc_height, box_details[i])

        # Update the x position for the next box
        x_position += box_width + space_between_boxes


def create_pdf(file_path):
    # Create a BytesIO buffer to capture the PDF content
    buffer = BytesIO()
    # Create a PDF document
    pdf = canvas.Canvas(file_path, pagesize=letter)

    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE START
    title(pdf, text="REPORT KPI MESE 2023", y_offset=680)
    # TITLE END

    # DESCRIPTIONS START
    descriptions(pdf, text_1="Autore del report: Christian Trocino", text2="Dati aggiornati al XX/XX/XXXX", x_offset=50,
                 y_offset=650)
    # DESCRIPTIONS END

    # TITLE_2 START
    title(pdf, text="PERIODO DI RIFERIMENTO: MESE 2023", y_offset=600)
    # TITLE_2 END

    # BOX_1 START
    #TAKE ALL THE VALUES FROM DATA TO SCORE
    tot_prev_evasi_mese = data_to_score.n_tot_prev_evasi_mese()
    tot_prev_acc_mese = data_to_score.n_tot_prev_accettati_mese()
    tot_prev_acc_cons = data_to_score.prev_acc_consuntivo()
    tot_prev_evasi_tot = data_to_score.importo_tot_prev_evasi()

    num_boxes = 4
    box_titles = ["N. Tot. Prev. Evasi", "N. Tot. Prev. Accettati", "N. Tot. Prev. Acc. consuntivo ",
                  "Importo. Tot. Prev. Evasi"]
    box_values = [str(tot_prev_evasi_mese), str(tot_prev_acc_mese), str(tot_prev_acc_cons), str(tot_prev_evasi_tot)]
    box_width = 120
    box_height = 80

    draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset=480)
    # BOX_1 END

    #TITLE_3 START
    title(pdf, text="PERIODO DI RIFERIMENTO: ANNO 2023", y_offset=450)
    # TITLE_3 END

    # BOX_2 START
    # TAKE ALL THE VALUES FROM DATA TO SCORE
    tot_prev_acc = data_to_score.n_tot_prev_accettati_anno()
    tot_prev_acc_importo = data_to_score.importo_tot_prev_accettati()


    num_boxes = 2
    box_titles = ["N. Tot. Prev. Accettati", "Importo. Tot. Prev. Accettati"]
    box_values = [str(tot_prev_acc), str(tot_prev_acc_importo)]
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
    box_titles = ["FATTURATO AD OGGI", "FATTURATO DA EMETTERE", "FATTURATO PREVISTO 2023"]
    box_values = [str(fatturato_ad_oggi), str(fatturato_da_emettere), str(fatturato_previsto)]
    box_width = 120
    box_height = 80

    draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset=240)
    # BOX_3 END




    # FOOTER START
    footer(pdf)
    # FOOTER END
########################################################################################################################
    # SECOND PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE_3 START
    title(pdf, text="ANALISI OPERATIVA PROGETTI", y_offset=680)
    # TITLE_3 END

    # DESCRIPTIONS + IMG START

    descriptions(pdf, text_1="N Progetti in progress su PM", text2="", x_offset=50, y_offset=660)
    # Draw Altair chart image under the description
    chart_path = data_to_chart.n_progetti_in_progress_su_pm("", "")
    #chart_path = r'pngs_of_charts/chart_1.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=670, logo_width=450, logo_height=200)

    descriptions(pdf, text_1="Importi Progetti in progress per ANNO", text2="", x_offset=50, y_offset=450)
    chart_path = data_to_chart.importi_progress_pm("", "")
    #chart_path = r'C:\Users\raffaele.loglisci\PycharmProjects\pdf_heroku\monday_data_extraction\pngs_of_charts\chart_2.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=465, logo_width=450, logo_height=180)

    descriptions(pdf, text_1="Importo Progetti in progress per BU", text2="", x_offset=50, y_offset=250)
    chart_path = data_to_chart.importo_progress_bu("", "")
    #chart_path = r'C:\Users\raffaele.loglisci\PycharmProjects\pdf_heroku\monday_data_extraction\pngs_of_charts\chart_3.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=265, logo_width=450, logo_height=130)

    # DESCRIPTIONS + IMG END

    # FOOTER START
    footer(pdf)
    # FOOTER END

    # SECOND PAGE END
########################################################################################################################
    # THIRD PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE_4 START
    title(pdf, text="CONTROLLO DI GESTIONE", y_offset=680)
    # TITLE_4 END

    # DESCRIPTIONS + IMG START

    descriptions(pdf, text_1="Analisi Ferie - Malattia - Dayhospital - Dipendenti", text2="", x_offset=50, y_offset=660)
    # Draw Altair chart image under the description
    chart_path = data_to_chart.analisi_ferie_malattia()
    #chart_path = r'pngs_of_charts/chart_4.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=670, logo_width=450, logo_height=200)

    descriptions(pdf, text_1="Analisi Permessi/ROL Dipendenti", text2="", x_offset=50, y_offset=450)
    chart_path = data_to_chart.analisi_permessi_rol()
    #chart_path = r'pngs_of_charts\chart_5.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=465, logo_width=450, logo_height=180)

    descriptions(pdf, text_1="Analisi giornate Smart Working", text2="", x_offset=50, y_offset=250)
    chart_path = data_to_chart.giornate_smart_working()
    #chart_path = r'pngs_of_charts\chart_6.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=265, logo_width=450, logo_height=130)


    # DESCRIPTIONS + IMG END


    # FOOTER START
    footer(pdf)
    # FOOTER END
    # THIRD PAGE END

########################################################################################################################

    # FOURTH PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE_4 START
    title(pdf, text="CONTROLLO DI GESTIONE", y_offset=680)
    # TITLE_4 END

    # DESCRIPTIONS + IMG START

    descriptions(pdf, text_1="Analisi Assenze Liberi Professionisti", text2="", x_offset=50, y_offset=660)
    # Draw Altair chart image under the description
    chart_path = data_to_chart.analisi_assenze_liberi_professionisti()
    #chart_path = r'pngs_of_charts/chart_7.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=670, logo_width=450, logo_height=200)

    descriptions(pdf, text_1="Timesheet Mese", text2="", x_offset=50, y_offset=450)
    chart_path = data_to_chart.timesheet_mese()
    #chart_path = r'pngs_of_charts\chart_8.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=465, logo_width=450, logo_height=180)

    descriptions(pdf, text_1="BU/h", text2="", x_offset=50, y_offset=250)
    chart_path = data_to_chart.bu_h_pie()
    #chart_path = r'pngs_of_charts\chart_9.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=265, logo_width=450, logo_height=130)

    # DESCRIPTIONS + IMG END

    # FOOTER START
    footer(pdf)
    # FOOTER END
    # FOURTH PAGE END
# ########################################################################################################################
    # FIFTH PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    descriptions(pdf, text_1="Resoconto Budget Consuntivo Per Player", text2="", x_offset=50, y_offset=660)
    # Draw Altair chart image under the description
    chart_path = data_to_chart.resoconto_budget_consuntivo_player()
    #chart_path = r'pngs_of_charts/chart_7.png'
    draw_chart_under_description(pdf, chart_path, x_offset=None, y_offset=670, logo_width=450, logo_height=200)

    # BOX_1 START

    num_boxes = 2
    box_titles = ["OBIETTIVI 2023", "COMMENTI"]
    box_values = ["TESTO", "TESTO"]
    box_width = 220
    box_height = 80

    draw_boxes(pdf, num_boxes, box_titles, box_values, box_width, box_height, current_y_offset=300)
    # BOX_1 END


    # FOOTER START
    footer(pdf)
    # FOOTER END
    # FIFTH PAGE END
########################################################################################################################
    # SIXT PAGE START
    pdf.showPage()
    # HEADER START
    header(pdf)
    #HEADER END


    # TITLE_4 START
    title(pdf, text="REPORT PM KPI: Lelenia Cacioppo", y_offset=680)
    # TITLE_4 END

    # DESCRIPTIONS + IMG START
    #LEFT
    descriptions(pdf, text_1="Numero Progetti In Progress", text2="", x_offset=50, y_offset=660)
    # Draw Altair chart image under the description
    chart_path = data_to_chart.n_progetti_in_progress_su_pm('Chiara Bernacchi', 'chart_chiara.png')
    #chart_path = r'pngs_of_charts/chart_chiara.png'
    draw_chart_under_description(pdf, chart_path, x_offset=50, y_offset=670, logo_width=225, logo_height=130)

    descriptions(pdf, text_1="Fatturazione Progetti In Progress (Media)", text2="", x_offset=50, y_offset=500)
    chart_path = data_to_chart.fatturazione_in_progress_media('Chiara Bernacchi', 'fatturazione_in_progress_media_chiara.png')
    #chart_path = r'pngs_of_charts\fatturazione_in_progress_media_chiara.png'
    draw_chart_under_description(pdf, chart_path, x_offset=40, y_offset=500, logo_width=225, logo_height=130)

    descriptions(pdf, text_1="Numero Progetti in progress Per Anno", text2="", x_offset=50, y_offset=310)
    chart_path = data_to_chart.numero_progetti_in_progress_anno()
    #chart_path = r'pngs_of_charts\chart_13.png'
    draw_chart_under_description(pdf, chart_path, x_offset=50, y_offset=310, logo_width=205, logo_height=130)
    #LEFT


    #RIGHT
    descriptions(pdf, text_1="Importi Progetti In Progress per PM", text2="", x_offset=350, y_offset=660)
    # Draw Altair chart image under the description
    chart_path = data_to_chart.importi_progress_pm("Chiara Bernacchi", "importi_progress_pm_chiara.png")
    #chart_path = r'pngs_of_charts/importi_progress_pm_chiara.png'
    draw_chart_under_description(pdf, chart_path, x_offset=350, y_offset=670, logo_width=225, logo_height=130)

    descriptions(pdf, text_1="Importo Progetti in Progress per BU", text2="", x_offset=350, y_offset=500)
    chart_path = data_to_chart.importo_progress_bu(["FM0","CONS-IMP", "CONS-IMM"], "importo_progress_bu.png")
    #chart_path = r'pngs_of_charts\importo_progress_bu.png'
    draw_chart_under_description(pdf, chart_path, x_offset=350, y_offset=500, logo_width=225, logo_height=130)

    descriptions(pdf, text_1="Importo Progetti in progress Per Anno", text2="", x_offset=350, y_offset=310)
    chart_path = data_to_chart.importo_progetti_progress_anno(["2020", "2021", "2022", "2023"], "importo_progetti_progress_anno_filtered.png")
    #chart_path = r'pngs_of_charts\importo_progetti_progress_anno_filtered.png'
    draw_chart_under_description(pdf, chart_path, x_offset=350, y_offset=310, logo_width=205, logo_height=130)
    #RIGHT

    # DESCRIPTIONS + IMG END



    # FOOTER START
    footer(pdf)
    # FOOTER END
    # SIXT PAGE END

########################################################################################################################
    # SEVENTH PAGE START

    pdf.showPage()
    # HEADER START
    header(pdf)
    # HEADER END

    # TITLE START
    title(pdf, text="REPORT PM  Dettaglio: Lelenia Cacioppo", y_offset=680)
    # TITLE END

    # Create boxes with descriptions
    n_boxes = 7  # Adjust the number of boxes as needed
    box_details = [
        (" Numero GU\n lavorate nel\n mese corrente"),
        (" Contratto\n SI/NO"),
        (" N Progetto"),
        (" Imponibile "),
        (" Fatturato"),
        (" Da Fatturare"),
        (" Data Prevista\n Chiusura")
    ]

    create_boxes(pdf, n_boxes, box_details, x_offset=0, desc_height=40, y_offset=550)

    # Create multiple sets of boxes with descriptions
    num_sets = 4  # Adjust the number of sets as needed
    box_descriptions(pdf, x_offset=0, y_offset=515, num_sets=num_sets)

    # FOOTER START
    footer(pdf)
    # FOOTER END
    # SEVENTH PAGE END
########################################################################################################################

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








