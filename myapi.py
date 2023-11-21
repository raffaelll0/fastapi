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
import json
from fastapi.responses import JSONResponse
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
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

@app.get("/webhook")
def monday_webhook(request):
    """
    THIS VIEW IS ACTIVATED WHEN A WEBHOOK IS SENT FROM MONDAY.COM
    IT TAKES THE REQUEST, PARSE IT AS JSON
    CHECKS IF THERE'S A DICTIONARY WITH A CHALLENGE KEY AND A VALUE
    IF IT EXISTS IT SENDS IT BACK, IF CORRECT, THE CONNECTION IS TRUE

    WE THEN USE THE DATA OF THE WEBHOOK TO EXTRACT VALUES FROM A BOARD
    (THIS IS DONE WHEN data_extraction() IS CALLED)

    Args:
        data: parsed json of the data that the webhook gives
        challenge: is in a dictionary and contains a value(int)
        data_extraction(): a function that extracts data via api req
        nome, cognome, p_iva: values taken from data_extraction()
        pdf_view(): is called once the webhook is true,
                    to upload the pdf in monday

    Returns:
        THIS VIEW RETURNS THE CHALLENGE TO MONDAY.COM,
        THE webhook.html AND A MESSAGE ON THE WEBPAGE
    """
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # manage first call from monday.com by sending the challenge token back
            challenge = data.get('challenge')
            if challenge:
                # Respond with the challenge to verify the connection
                return JSONResponse({'challenge': challenge})


            #upload_pdf_to_monday(pdf_path, id_polizza)
            #print("pdf uploaded to monday!")

        except Exception as e:
            return JSONResponse({'error': str(e)}, status=500)


def webhook():
    pdfpath = generate_pdf()
    upload_pdf_to_monday(pdfpath, boardId)


