from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from io import BytesIO

from monday_data_extraction import main
from monday_data_extraction.data_to_score import *
from monday_data_extraction.data_to_chart import *

def pdf_title_func(title, story):
    # CREO UN TITOLO PER LA NUOVA PAGINA
    title = title
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    story.append(title_paragraph)
    story.append(Spacer(1, 12))


def save_pdf_to_file(pdf_bytes, filename):
    with open(filename, "wb") as pdf_file:
        pdf_file.write(pdf_bytes)


def generate_pdf(prev_evasi_mes):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    ########################################################################################################################
    # PRIMA PAGINA DEL PDF

    # CREO UNA LISTA PER SALVARE INFORMAZIONI
    story = []

    pdf_title_func("REPORT KPI MESE 2023", story)

    # AGGIUNGO I DATI DELL'AUTORE E GLI AGGIORNAMENTI
    author_info = "Autore del report: Christian Trocino<br/>Dati aggiornati al XX/XX/XXXX"
    author_style = getSampleStyleSheet()["Normal"]
    author_paragraph = Paragraph(author_info, author_style)
    story.append(author_paragraph)

    # CREO UNA LINEA DI SPAZIO SOTTO IL TITOLO
    story.append(Spacer(1, 12))

    ########################################################

    pdf_title_func("PERIODO DI RIFERIMENTO MESE 2023", story)

    # CREO UNA DESCRIZIONE PER OGNI BOX
    description1 = "N tot prev.Evasi"
    description2 = "N tot prev.Accettati"
    description3 = "N tot prev.acc.consuntivo"
    description4 = "Importo tot prev.Evasi"

    # CREO UNA TABELLA CON 4 QUADRATI CHE CONTENGONO DATI
    data = [
        [description1, description2, description3, description4],
        [str(prev_evasi_mes), "str(prev_acc_mes)", "str(prev_acc_consuntivo)", "str(importo_tot_prev_evasi)"]
    ]

    table_data = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data]
    table = Table(table_data, colWidths=100, rowHeights=50)  # Decreased row heights

    # APPLICO LO STILE DELLE TABELLE PER UNO SFONDO BIANCO E LINEE NERE
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SIZE', (0, 0), (-1, -1), 36),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(table)

    # CREO UNA LINEA DI SPAZIO SOTTO IL TITOLO
    story.append(Spacer(1, 12))

    ###################################################

    pdf_title_func("PERIODO DI RIFERIMENTO: ANNO 2023", story)

    # CREO UNA TABELLA CON 2 BOX CONTENTI I VALORI 1 ALLA SINISTRA E 2 ALLA DESTRA (PER ADESSO)
    data2 = [
        ["N. Tot.Prev.Accettati nell'anno", "Importo Tot.Prev.Accettati"],
        ["str(prev_acc_anno)", "str(importo_tot_prev_accettati)"]
    ]

    table_data2 = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data2]
    table2 = Table(table_data2, colWidths=100, rowHeights=50)  # Decreased row heights

    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SIZE', (0, 0), (-1, -1), 36),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(table2)

    # CREO UNA LINEA DI SPAZIO SOTTO IL TITOLO
    story.append(Spacer(1, 12))

    ################################################

    # AGGIUNGO LA DESCRIZIONE "FATTURATO AD OGGI," "FATTURATO DA EMETTERE," E "FATTURATO PREVISTO 2023"
    # SOTTO LE BOX ESISTENTI
    description_left = "FATTURATO AD OGGI"
    description_center = "FATTURATO DA EMETTERE"
    description_right = "FATTURATO PREVISTO 2023"

    # CCREO UNA TABELLA CON TRE BOX CONTENENTI VALORI E DESCRIZIONI
    data3 = [
        [description_left, description_center, description_right],
        ["str(fatturato_ad_oggi)", "str(fatturato_da_emettere)", "str(fatturato_prev_2023)"]
    ]

    table_data3 = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data3]
    table3 = Table(table_data3, colWidths=100, rowHeights=50)  # Decreased row heights

    table3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SIZE', (0, 0), (-1, -1), 36),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(table3)

    ########################################################################################################################
    # SECONDA PAGINA DEL PDF

    # AGGIUNGO UN PAGE BREAK PER INIZIARE UNA NUOVA PAGINA
    story.append(PageBreak())

    pdf_title_func("ANALISI OPERATIVA PROGETTI", story)



    ########################################################################################################################

    # Build the PDF document
    doc.build(story)

    # Save the PDF to a file
    save_pdf_to_file(buffer.getvalue(), "output.pdf")


    buffer.seek(0)
    return buffer.read()



# Create a function to generate the PDF
# def generate_pdf(prev_evasi_mes,
#                  prev_acc_mes,
#                  prev_acc_consuntivo,
#                  importo_tot_prev_evasi,
#                  prev_acc_anno,
#                  importo_tot_prev_accettati,
#                  fatturato_prev_2023,
#                  fatturato_ad_oggi,
#                  fatturato_da_emettere,
#                  chart_progetti_in_progress_su_pm,
#                  importo_progetti_progress_anno,
#                  portafoglio_ordine_residuo,
#                  analisi_ferie_malattia,
#                  analisi_permessi_rol,
#                  analisi_assenze_liberi_professionisti,
#                  giornate_smart_working,
#                  timesheet_mese,
#                  bu_h_pie):
#     """
#     Questa funzione crea un pdf basato da griglie rettangolari con
#     all' interno i dati estrapolati da varie funzioni presenti nel file extract_data_script
#     (Per esempio la parte iniziale aggiunge delle descrizioni con delle box sotto)
#
#     il file creato si chiama kpi_report.pdf e si trova all'interno della root di progetto
#
#     Args:
#
#     Returns:
#         pdf file
#     """
#
#
# ########################################################################################################################
# #PRIMA PAGINA DEL PDF
#
#     # CREO UN OGGETTO SimpleDocTemplate
#     doc = SimpleDocTemplate(r"C:\Users\raffaele.loglisci\Desktop\altair_demo\kpi_report.pdf", pagesize=letter)
#
#     # CREO UNA LISTA PER SALVARE INFORMAZIONI
#     story = []
#
#     pdf_title_func("REPORT KPI MESE 2023", story)
#
#
#     # AGGIUNGO I DATI DELL'AUTORE E GLI AGGIORNAMENTI
#     author_info = "Autore del report: Christian Trocino<br/>Dati aggiornati al XX/XX/XXXX"
#     author_style = getSampleStyleSheet()["Normal"]
#     author_paragraph = Paragraph(author_info, author_style)
#     story.append(author_paragraph)
#
#     # CREO UNA LINEA DI SPAZIO SOTTO IL TITOLO
#     story.append(Spacer(1, 12))
#
#
# ########################################################
#
#     pdf_title_func("PERIODO DI RIFERIMENTO MESE 2023", story)
#
#
#
#     # CREO UNA DESCRIZIONE PER OGNI BOX
#     description1 = "N tot prev.Evasi"
#     description2 = "N tot prev.Accettati"
#     description3 = "N tot prev.acc.consuntivo"
#     description4 = "Importo tot prev.Evasi"
#
#
#
#     # CREO UNA TABELLA CON 4 QUADRATI CHE CONTENGONO DATI
#     data = [
#         [description1, description2, description3, description4],
#         [str(prev_evasi_mes), str(prev_acc_mes), str(prev_acc_consuntivo), str(importo_tot_prev_evasi)]
#     ]
#
#     table_data = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data]
#     table = Table(table_data, colWidths=100, rowHeights=50)  # Decreased row heights
#
#     # APPLICO LO STILE DELLE TABELLE PER UNO SFONDO BIANCO E LINEE NERE
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('SIZE', (0, 0), (-1, -1), 36),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
#
#     story.append(table)
#
#     # CREO UNA LINEA DI SPAZIO SOTTO IL TITOLO
#     story.append(Spacer(1, 12))
#
#
# ###################################################
#
#     pdf_title_func("PERIODO DI RIFERIMENTO: ANNO 2023", story)
#
#
#     # CREO UNA TABELLA CON 2 BOX CONTENTI I VALORI 1 ALLA SINISTRA E 2 ALLA DESTRA (PER ADESSO)
#     data2 = [
#         ["N. Tot.Prev.Accettati nell'anno", "Importo Tot.Prev.Accettati"],
#         [str(prev_acc_anno), str(importo_tot_prev_accettati)]
#     ]
#
#     table_data2 = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data2]
#     table2 = Table(table_data2, colWidths=100, rowHeights=50)  # Decreased row heights
#
#     table2.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('SIZE', (0, 0), (-1, -1), 36),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
#
#
#     story.append(table2)
#
#     # CREO UNA LINEA DI SPAZIO SOTTO IL TITOLO
#     story.append(Spacer(1, 12))
#
#
# ################################################
#
#
#     # AGGIUNGO LA DESCRIZIONE "FATTURATO AD OGGI," "FATTURATO DA EMETTERE," E "FATTURATO PREVISTO 2023"
#     # SOTTO LE BOX ESISTENTI
#     description_left = "FATTURATO AD OGGI"
#     description_center = "FATTURATO DA EMETTERE"
#     description_right = "FATTURATO PREVISTO 2023"
#
#     # CCREO UNA TABELLA CON TRE BOX CONTENENTI VALORI E DESCRIZIONI
#     data3 = [
#         [description_left, description_center, description_right],
#         [str(fatturato_ad_oggi), str(fatturato_da_emettere), str(fatturato_prev_2023)]
#     ]
#
#     table_data3 = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data3]
#     table3 = Table(table_data3, colWidths=100, rowHeights=50)  # Decreased row heights
#
#     table3.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('SIZE', (0, 0), (-1, -1), 36),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
#
#     story.append(table3)
#
#
# ########################################################################################################################
# #SECONDA PAGINA DEL PDF
#
#     # AGGIUNGO UN PAGE BREAK PER INIZIARE UNA NUOVA PAGINA
#     story.append(PageBreak())
#
#     pdf_title_func("ANALISI OPERATIVA PROGETTI", story)
#
#
#     pdf_title_func("Progetti in progress su PM", story)
#     # Add the Altair chart image to the story
#     img = Image(chart_progetti_in_progress_su_pm)
#     story.append(img)
#
#
#     story.append(PageBreak())
#     pdf_title_func("Importo progetti in progress per anno", story)
#     # Add the Altair chart image to the story
#     img_2 = Image(importo_progetti_progress_anno)
#     story.append(img_2)
#
#     story.append(PageBreak())
#     pdf_title_func("portafoglio ordine residuo", story)
#     # Add the Altair chart image to the story
#     img_3 = Image(portafoglio_ordine_residuo)
#     story.append(img_3)
#
#
#
#
#
#     ########################################################################################################################
# #TERZA PAGINA DEL PDF
#
#
#     # Add a page break to start a new page
#     story.append(PageBreak())
#
#     pdf_title_func("analisi ferie malattia", story)
#     # Add the Altair chart image to the story
#     img_4 = Image(analisi_ferie_malattia)
#     story.append(img_4)
#
#     story.append(PageBreak())
#     pdf_title_func("analisi permessi rol", story)
#     # Add the Altair chart image to the story
#     img_5 = Image(analisi_permessi_rol)
#     story.append(img_5)
#
#     story.append(PageBreak())
#     pdf_title_func("analisi assenze liberi professionisti", story)
#     # Add the Altair chart image to the story
#     img_6 = Image(analisi_assenze_liberi_professionisti)
#     story.append(img_6)
#
#     story.append(PageBreak())
#     pdf_title_func("giornate smart working", story)
#     # Add the Altair chart image to the story
#     img_7 = Image(giornate_smart_working)
#     story.append(img_7)
#
#     story.append(PageBreak())
#     pdf_title_func("timesheet mese", story)
#     # Add the Altair chart image to the story
#     img_8 = Image(timesheet_mese)
#     story.append(img_8)
#
#     story.append(PageBreak())
#     pdf_title_func("bu/h", story)
#     # Add the Altair chart image to the story
#     img_9 = Image(bu_h_pie)
#     story.append(img_9)
#
#
#
#
# ########################################################################################################################
# #QUARTA PAGINA DEL PDF
#
#     story.append(PageBreak())
#     # Create a title for the second page
#     third_page_title = "CONTROLLO DI GESTIONE"
#     third_page_title_style = getSampleStyleSheet()["Title"]
#     third_page_title_paragraph = Paragraph(third_page_title, third_page_title_style)
#     story.append(third_page_title_paragraph)
#
#     # Add some space below the second page title
#     story.append(Spacer(1, 12))
#
#     # Add some space below the fourth page title
#     story.append(Spacer(1, 12))
#
#     # Add the "OBIETTIVI 2023" and "COMMENTI" boxes
#     data_objectives_comments = [
#         ["OBIETTIVI 2023", "COMMENTI"],
#         ["XXX", "XXX"]
#     ]
#
#     table_data_objectives_comments = [[Paragraph(cell, getSampleStyleSheet()["Normal"]) for cell in row] for row in data_objectives_comments]
#     table_objectives_comments = Table(table_data_objectives_comments, colWidths=[300, 300], rowHeights=[50, 50])
#
#     table_objectives_comments.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('SIZE', (0, 0), (-1, -1), 36),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
#
#     story.append(table_objectives_comments)
#
#
# ########################################################################################################################
#
#     # Build the PDF document
#     doc.build(story)

#     return buffer.read()
#
#
#
# if __name__ == "__main__":
#     generate_pdf()







