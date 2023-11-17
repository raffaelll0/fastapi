from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from io import BytesIO

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter



app = FastAPI()


@app.get("/download_blank_pdf")
def download_blank_pdf():
    # Generate a blank PDF
    pdf_bytes = generate_pdf()

    # Return the PDF as a response
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=blank.pdf"})

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


def generate_pdf():
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
        ["str(prev_evasi_mes)", "str(prev_acc_mes)", "str(prev_acc_consuntivo)", "str(importo_tot_prev_evasi)"]
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
    #save_pdf_to_file(buffer.getvalue(), "output.pdf")


    buffer.seek(0)
    return buffer.read()
generate_pdf()



