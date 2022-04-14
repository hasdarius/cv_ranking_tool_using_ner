import os
import pdfplumber
import spacy

import train_custom_ner
from os.path import isfile, join
from os import path, listdir
from constants import CONCEPTS_SCORES


def get_max_seniority(list_of_seniorities):
    # print(list_of_seniorities)
    seniority_priority_list = ['senior', 'mid', 'junior', 'intern']
    final_seniority_priority_list = ['senior', 'mid', 'junior', 'intern']
    for priority in seniority_priority_list:
        if priority not in list_of_seniorities:
            final_seniority_priority_list.remove(priority)
    return final_seniority_priority_list[0]


def get_cv_ranking_score(cv_entities_dictionary, job_description_entities_dictionary):
    max_required_seniority = get_max_seniority(
        list(map(lambda x: x.lower(), job_description_entities_dictionary['Seniority'])))
    max_given_seniority = get_max_seniority(list(map(lambda x: x.lower(), cv_entities_dictionary['Seniority'])))
    score = CONCEPTS_SCORES[max_given_seniority]['Seniority']
    print("Max required seniority: " + max_required_seniority)
    print("Max given seniority: " + max_given_seniority)
    max_absolute_seniority = get_max_seniority([max_required_seniority, max_given_seniority])
    print("Max absolute seniority: " + max_absolute_seniority)
    for label in job_description_entities_dictionary:
        if label != 'Seniority':
            required_label_values_list = job_description_entities_dictionary[label]
            given_label_values_list = cv_entities_dictionary[label]
            max_values = max(2 * len(required_label_values_list),
                             CONCEPTS_SCORES[max_absolute_seniority]['Max ' + label])
            overflow = len(given_label_values_list) - max_values
            if overflow > 0:
                score -= overflow * CONCEPTS_SCORES[max_required_seniority]['Full ' + label]
            for given_label_value in given_label_values_list:
                if given_label_value in required_label_values_list:
                    score += CONCEPTS_SCORES[max_required_seniority]['Full ' + label]
                    print("Full: " + given_label_value)
                else:
                    score += CONCEPTS_SCORES[max_required_seniority]['Partial ' + label]
                    print("Partial: " + given_label_value)
    return score


def generate_dictionary_of_concepts(doc):
    final_dictionary = {}
    for ent in doc.ents:
        final_dictionary.setdefault(ent.label_, []).append(ent.text)
    print(final_dictionary)
    return final_dictionary


def read_cv_entities_from_pdf(document_path, nlp):
    pdf = pdfplumber.open(document_path)
    text = ""
    for page in pdf.pages:
        text = text + "\n" + page.extract_text()
    doc = nlp(text)
    return generate_dictionary_of_concepts(doc)


def read_cv_entities_from_txt(document_path, nlp):
    text_file = open(document_path, "r")
    text = text_file.read()
    doc = nlp(text)
    return generate_dictionary_of_concepts(doc)


def rank_cvs(job_description_text, cv_folder, model):
    custom_nlp = spacy.load(model)
    nlp_doc = custom_nlp(job_description_text)
    job_description_entities = generate_dictionary_of_concepts(nlp_doc)  # read dictionary entities
    cv_files = [file for file in listdir(cv_folder) if isfile(join(cv_folder, file))]
    score_list = []
    for cv_file in cv_files:
        _, file_extension = os.path.splitext(cv_file)
        match file_extension:
            case ".pdf":
                cv_entities_dictionary = read_cv_entities_from_pdf(cv_file, custom_nlp)
            case ".txt":
                cv_entities_dictionary = read_cv_entities_from_txt(cv_file, custom_nlp)
            case _:
                cv_entities_dictionary = {}  # here would be better to throw exception, decide with David
        cv_score = get_cv_ranking_score(cv_entities_dictionary, job_description_entities)
        score_list.append((cv_file, cv_score))
    return score_list.sort(key=lambda cv: cv[1])


if __name__ == "__main__":
    # main("Data/it_dataset.csv")
    nlp = spacy.load(train_custom_ner.CUSTOM_SPACY_MODEL)
    doc = nlp("I am a Java Software decveloper specialized in Spring, Docker, JUnit and Git.")
    generate_dictionary_of_concepts(doc)


def main(input_file):
    if not path.exists(train_custom_ner.CUSTOM_SPACY_MODEL):
        json_file_name = train_custom_ner.csv_to_json_with_labels(input_file, '-')
        training_data = train_custom_ner.json_to_spacy_format(json_file_name)
        train_custom_ner.fine_tune_and_save_custom_model(training_data,
                                                         new_model_name='technology_it_model',
                                                         output_dir=train_custom_ner.CUSTOM_SPACY_MODEL)
    # here we will test the model
