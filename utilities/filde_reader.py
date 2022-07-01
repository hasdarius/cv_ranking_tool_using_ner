import re

import pdfplumber

from utilities.constants import LABELS_LIST


def read_cv_entities_from_pdf(document_path, nlp):
    pdf = pdfplumber.open(document_path)
    text = ""
    for page in pdf.pages:
        text = text + "\n" + page.extract_text()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    doc = nlp(text)
    return generate_dictionary_of_concepts(doc)


def read_cv_entities_from_txt(document_path, nlp):
    text_file = open(document_path, "r")
    text = text_file.read()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    doc = nlp(text)
    return generate_dictionary_of_concepts(doc)


def generate_dictionary_of_concepts(doc):
    final_dictionary = {}
    for ent in doc.ents:
        final_dictionary.setdefault(ent.label_, set()).add(ent.text.lower().strip())
    detected_keys = final_dictionary.keys()
    for label in LABELS_LIST:
        if label not in detected_keys:
            final_dictionary[label] = set()
    print('This is the dictionary of concepts:')
    print(final_dictionary)
    print('-----------------------------------------------------')

    return final_dictionary
