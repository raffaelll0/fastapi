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
from monday_data_extraction.monday import *


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
            #pdf_bytes = open(pdf_path, "rb").read()
            return pdf_path    #StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf",headers={"Content-Disposition": "attachment;filename=blank.pdf"})
            switch = 1
        else:
            return {"message": "PDF is not ready yet. Try again later."}


def upload_pdf_to_monday(pdf_path:str):
    """
    THIS FUNCTION MAKES A QUERY TO THE ITEM ID WE PREVIOUSLY HAVE CLICKED(BTN)
    DEFINES IN WICH COLUMN TO UPLOAD THE PDF, (IN THIS CASE 'file')
    AND THEN USES THE PATH OF THE PDF IN THE pdf_view, THIS FUNCTION WORKS IF IT
    IS CALLED IN THE pdf_view SINCE WE HAVE THE PATH INSIDE OF IT


    Args:
        apiKey: key to access monday.com via api
        apiUrl: url of monday.com
        headers: returns a keyvalue dictionary with the api key
        query: this defines the steps to ad  the file with in the specific column
        payload: via query it defines where to upload the file



    Returns:
         response

    """
    print("upload pdf....")


    query = 'mutation($file: File!) {add_file_to_column(file: $file, item_id: 4494285664, column_id: "file") {id}}'
    data = {'query': query}
    files = [('variables[file]', ('hello.pdf', open(pdf_path,'rb'),'contenttype'))]
    response = requests.request("POST", apiUrl, headers=headers, data=data, files=files)


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        challenge = data.get('challenge')

        if challenge:
            return JSONResponse(content={'challenge': challenge})

        pdf_path = generate_pdf()
        # Add your logic for handling the POST request here
        upload_pdf_to_monday(pdf_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







