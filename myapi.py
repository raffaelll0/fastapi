import os
import time
from fastapi import FastAPI, BackgroundTasks
from monday_data_extraction import pdf_gen
import requests
from datetime import datetime


def is_first_day_of_month():
    today = datetime.now().day
    return today == 1


app = FastAPI()


def generate_pdf_task(file_path: str):
    # Simulate a long-running task (replace with your actual PDF generation logic)
    time.sleep(60)
    pdf_bytes = pdf_gen.create_pdf(file_path=file_path)
    return pdf_bytes


def upload_pdf_to_monday(pdf_path):

    url = "https://api.monday.com/v2/file"

    payload = {'query': 'mutation add_file($file: File!) {add_file_to_column (item_id: 4494041652, column_id:"file" '
                        'file: $file) {id}}', 'map': '{"image":"variables.file"}'}
    files = [
        ('image', ('report_da_aggiornare.pdf', open(pdf_path, 'rb'), 'application/pdf'))
    ]

    headers = {
        'Authorization': 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE0NTc5NTQ4MywiYWFpIjoxMSwidWlkIjoyNzk4NzQzMywiaWFkIjoiMjAyMi0wMi0xNFQwODoyOTo0NC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTExOTUwMTIsInJnbiI6InVzZTEifQ.j052k96lwfIBOtLGWng2xmZul4c_rWnguMOTduJ95DM',
        'Cookie': '__cf_bm=ZTReat.Jh1QkxowH5_Cmk7bZDpq6uFgjxdfrZNlLd7A-1700643090-0-ASmZC5ZBA5fxS+mIJ1iNrSTCn/SewsIy25w1YAjf3+fZrUAlosoXMsAZKJXhgDZda7vmP8EdLTPXf0yri68AqbedOhMC4oFQ56at0xC63YYR'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)


@app.get("/generate_pdf")
def generate_pdf(background_tasks: BackgroundTasks):
    # Start the background task for PDF generation
    background_tasks.add_task(generate_pdf_task, file_path="pdf_with_image.pdf")
    pdf_path = "pdf_with_image.pdf"

    switch = 0

    while switch == 0:

        if os.path.exists(pdf_path) & is_first_day_of_month():
            upload_pdf_to_monday(pdf_path)
            return {"message": "PDF uploaded"}
            switch = 1

        else:
            return {"message": "PDF is not ready yet. Try again later."}












