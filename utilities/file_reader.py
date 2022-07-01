import re

import pdfplumber


def read_cv_entities_from_pdf(document_path, nlp):
    pdf = pdfplumber.open(document_path)
    text = ""
    for page in pdf.pages:
        text = text + "\n" + page.extract_text()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    return nlp(text)


def read_cv_entities_from_txt(document_path, nlp):
    text_file = open(document_path, "r")
    text = text_file.read()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    return nlp(text)
