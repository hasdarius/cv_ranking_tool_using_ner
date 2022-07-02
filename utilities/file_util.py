import re

import pdfplumber
import csv


def read_from_pdf(file_path):
    pdf = pdfplumber.open(file_path)
    text = ""
    for page in pdf.pages:
        text = text + "\n" + page.extract_text()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    return text


def read_from_txt(file_path):
    text_file = open(file_path, "r")
    text = text_file.read()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    return text


def write_tuple_list_to_csv(tuple_list, file_name):
    file = open(file_name, 'w', newline='')
    writer = csv.writer(file)
    writer.writerows(tuple_list)
