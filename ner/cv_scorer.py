import os
import re
from os import listdir
from os.path import isfile, join

import spacy

from ner import train_custom_ner
from utilities.business_ruler import apply_business_rules
from utilities.constants import CONCEPTS_SCORES, REASONING_PERFECT_MATCH, REASONING_PERFECT_MATCH_TYPE, \
    REASONING_GRAPH_CONNECTION_P1, REASONING_GRAPH_CONNECTION_P2, REASONING_GRAPH_CONNECTION_P3
from utilities.filde_reader import generate_dictionary_of_concepts, read_cv_entities_from_pdf, read_cv_entities_from_txt
from dbpedia.knowledge_graph import get_shortest_path_between_concepts, generate_knowledge_graph_components_from_files


def rank_cvs(job_description_text, cv_folder):
    graph = generate_knowledge_graph_components_from_files('./Data/edges.csv')
    custom_nlp = spacy.load(train_custom_ner.CUSTOM_SPACY_MODEL)
    job_description_text = re.sub(r"[^a-zA-Z0-9]", " ", job_description_text)
    nlp_doc = custom_nlp(job_description_text)
    job_description_entities = generate_dictionary_of_concepts(nlp_doc)  # read job description entities in dictionary
    cv_files = [file for file in listdir(cv_folder) if isfile(join(cv_folder, file))]
    score_list = []
    for cv_file in cv_files:
        _, file_extension = os.path.splitext(cv_file)
        feedback_list = []
        if file_extension == ".pdf":
            cv_entities_dictionary = read_cv_entities_from_pdf(cv_folder + '/' + cv_file, custom_nlp)
        else:
            if file_extension == ".txt":
                cv_entities_dictionary = read_cv_entities_from_txt(cv_folder + '/' + cv_file, custom_nlp)
            else:
                cv_entities_dictionary = {}
        cv_score = get_cv_ranking_score(cv_entities_dictionary, job_description_entities, feedback_list, graph)
        score_list.append((cv_file, cv_score, feedback_list))
    return sorted(score_list, key=lambda cv: cv[1], reverse=True)


def get_cv_ranking_score(cv_entities_dictionary, job_description_entities_dictionary, feedback_list, graph):
    max_required_seniority = get_max_seniority(
        list(map(lambda x: x.lower(), job_description_entities_dictionary['Seniority'])))
    max_given_seniority = get_max_seniority(list(map(lambda x: x.lower(), cv_entities_dictionary['Seniority'])))
    max_absolute_seniority = get_max_seniority([max_required_seniority, max_given_seniority])
    required_relevant_keys = ['Programming Language', 'Programming Concept', 'Tool/Framework']
    knowledge_graph_required_labels = [x for key in required_relevant_keys for x in
                                       job_description_entities_dictionary.get(key)]

    score = compute_score(cv_entities_dictionary, feedback_list, graph, job_description_entities_dictionary,
                          knowledge_graph_required_labels, max_absolute_seniority, max_given_seniority,
                          max_required_seniority)

    return score


def get_max_seniority(list_of_seniorities):
    seniority_priority_list = ['senior', 'mid', 'junior', 'intern']
    final_seniority_priority_list = ['senior', 'mid', 'junior', 'intern']
    for priority in seniority_priority_list:
        if priority not in list_of_seniorities:
            final_seniority_priority_list.remove(priority)
    if final_seniority_priority_list:
        return final_seniority_priority_list[0]
    return seniority_priority_list[1]  # None


def compute_score(cv_entities_dictionary, feedback_list, graph, job_description_entities_dictionary,
                  knowledge_graph_required_labels, max_absolute_seniority, max_given_seniority, max_required_seniority):
    score = 0
    if max_given_seniority is not None:
        score = CONCEPTS_SCORES[max_given_seniority]['Seniority']
    for label in job_description_entities_dictionary:
        if label != 'Seniority':
            required_label_values_list = job_description_entities_dictionary[label]
            given_label_values_list = cv_entities_dictionary[label]

            score += apply_business_rules(max_absolute_seniority, label,
                                          required_label_values_list,
                                          given_label_values_list, feedback_list)
            for given_label_value in given_label_values_list:
                if given_label_value in required_label_values_list:
                    score += CONCEPTS_SCORES[max_required_seniority]['Full ' + label]
                    feedback_list.append(
                        REASONING_PERFECT_MATCH + "<<" + given_label_value + ">>" + REASONING_PERFECT_MATCH_TYPE + label + ".")
                else:
                    score += score_partial_matches(feedback_list, given_label_value, graph,
                                                   knowledge_graph_required_labels, label, max_required_seniority)
    return score


def score_partial_matches(feedback_list, given_label_value, graph, knowledge_graph_required_labels, label,
                          max_required_seniority):
    for required_label_value in knowledge_graph_required_labels:
        shortest_path, nr_of_shortest_paths = get_shortest_path_between_concepts(
            given_label_value.lower(),
            required_label_value.lower(), graph)
        if shortest_path:
            reasoning = REASONING_GRAPH_CONNECTION_P1 + "<<" + required_label_value + ">>, <<" + given_label_value + ">>" + REASONING_GRAPH_CONNECTION_P2 + str(
                nr_of_shortest_paths) + REASONING_GRAPH_CONNECTION_P3
            for connection_tuple in shortest_path:
                reasoning = reasoning + "<<" + connection_tuple[0][0] + ">> which <<" + connection_tuple[1][
                    'relationship'] + ">> with <<" + connection_tuple[0][1] + ">>, "

            feedback_list.append(reasoning)
            return CONCEPTS_SCORES[max_required_seniority]['Partial ' + label]
    return 0
