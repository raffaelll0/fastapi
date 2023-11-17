from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from io import BytesIO

from monday_data_extraction.main import genera_report_hf


app = FastAPI()


@app.get("/download_report_pdf")
def download_report_pdf():
    # Call the function to generate the PDF
    pdf_bytes = genera_report_hf()

    # Return the generated PDF as a response
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=kpi_report.pdf"})
