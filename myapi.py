from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from io import BytesIO


app = FastAPI()


@app.get("/download_blank_pdf")
def download_blank_pdf():
    # Generate a blank PDF
    pdf_bytes = generate_blank_pdf()

    # Return the PDF as a response
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=blank.pdf"})


def generate_blank_pdf():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Set up your PDF content here
    p.drawString(100, 100, "This is a blank PDF.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.read()
