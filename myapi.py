# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
# from io import BytesIO
# from monday_data_extraction import pdf_gen
#
#
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# from io import BytesIO
# from monday_data_extraction import pdf_gen

#app = FastAPI()


# @app.get("/")
# def download_blank_pdf():
#     #call the genera pdf function in the main file
#     pdf_bytes = pdf_gen.create_pdf(file_path="pdf_with_image.pdf")
#     # Return the PDF as a response
#     return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=blank.pdf"})
#
# download_blank_pdf()


import os
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
from monday_data_extraction import pdf_gen


app = FastAPI()

def generate_pdf_task(file_path: str):
    # Simulate a long-running task (replace with your actual PDF generation logic)
    time.sleep(60)
    pdf_bytes = pdf_gen.create_pdf(file_path=file_path)
    return pdf_bytes

@app.get("/generate_pdf")
def generate_pdf(background_tasks: BackgroundTasks):
    # Start the background task for PDF generation
    background_tasks.add_task(generate_pdf_task, file_path="pdf_with_image.pdf")

    pdf_path = "pdf_with_image.pdf"
    switch = 0

    while switch == 0:

        if os.path.exists(pdf_path):
            pdf_bytes = open(pdf_path, "rb").read()
            return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf",
                                     headers={"Content-Disposition": "attachment;filename=blank.pdf"})
            switch = 1
        else:
            return {"message": "PDF is not ready yet. Try again later."}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        challenge = data.get('challenge')

        if challenge:
            return JSONResponse(content={'challenge': challenge})

        # Add your logic for handling the POST request here

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def webhook():
    pdfpath = generate_pdf()
    upload_pdf_to_monday(pdfpath, boardId)




