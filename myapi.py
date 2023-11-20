from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from monday_data_extraction import main


app = FastAPI()


@app.get("/")
def download_blank_pdf():
    #call the genera pdf function in the main file
    pdf_bytes = main.genera_pdf_prova()
    # Return the PDF as a response
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=blank.pdf"})

download_blank_pdf()






