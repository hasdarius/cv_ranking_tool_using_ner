import os
import re

import nest_asyncio
import pdfplumber

from rdf2g import rdflib, expand_tree, clear_graph
from rdf2g import setup_graph
from os import listdir
from os.path import isfile, join

from nlp_scorer.natural_text_to_graph.process_amr_rdf import read_graph_from_rdf_file, \
    transform_from_natural_text_to_rdf
from nlp_scorer.graph_similarity_algorithm.graph_score_reasoning import generate_score_explanation
from nlp_scorer.graph_similarity_algorithm.graph_similarity_algorithm import initialize_similarity_matrix, \
    apply_similarity_measure, get_graph_similarity
from utilities.file_util import read_from_txt

COMMON_KEY_LABELS = ['rdfs:comment', 'iri', 'rdfs:label', '@id', '@label', 'amr-core:root', 'amr-core:has-sentence',
                     'amr-core:has-id', 'amr-core:has-date']


def initialize_nodes_neighbours(node_list, node_matrix_mapping, nodes_neighbours):
    iter = 0
    for dict_node in node_list:
        nodes_neighbours.append({"iri": dict_node['iri'][0], "in-neighbours": [], "out-neighbours": []})
        node_matrix_mapping[dict_node['iri'][0]] = iter
        iter += 1


def set_in_out_nodes_of_node(node, node_dict_info, nodes_neighbours):
    out_nodes_list = []
    # print(node)
    for label in node.keys():
        # print("Label: " + str(label))
        if label not in COMMON_KEY_LABELS:
            out_nodes_list.append(node[label])
            if not isinstance(node[label], str):
                if isinstance(node[label], list):
                    for neighbour_dict in node[label]:
                        node_dict_info["out-neighbours"].append(neighbour_dict['iri'])
                        neighbour = list(filter(lambda ndi: ndi["iri"] == neighbour_dict['iri'], nodes_neighbours))
                        neighbour[0]["in-neighbours"].append(node['iri'])
                else:
                    node_dict_info["out-neighbours"].append(node[label]['iri'])
                    neighbour = list(filter(lambda ndi: ndi["iri"] == node[label]['iri'], nodes_neighbours))
                    neighbour[0]["in-neighbours"].append(node['iri'])


def construct_neighbours_structures(nodes_neighbours_graph, g):
    for node_dict_neighbour in nodes_neighbours_graph:
        traversal = g.V().has('iri', node_dict_neighbour['iri']).outE().inV().tree().next()
        nodes_info = expand_tree(g, traversal)
        if nodes_info:
            # pprint(nodes_info[0])
            set_in_out_nodes_of_node(nodes_info[0], node_dict_neighbour, nodes_neighbours_graph)


def gremlin_main(input_file1, input_file2):
    nest_asyncio.apply()
    nodes_neighbours_graph1 = []
    nodes_neighbours_graph2 = []
    node_matrix_mapping_graph1 = {}
    node_matrix_mapping_graph2 = {}

    DEFAULT_LOCAL_CONNECTION_STRING = "ws://localhost:8182/gremlin"
    g = setup_graph(DEFAULT_LOCAL_CONNECTION_STRING)
    rdf_graph = rdflib.Graph()

    node_list_g1 = read_graph_from_rdf_file(input_file1, g, rdf_graph)
    node_list_g1 = sorted(node_list_g1, key=lambda i: i['label'])
    initialize_nodes_neighbours(node_list_g1, node_matrix_mapping_graph1, nodes_neighbours_graph1)
    # pprint(nodes_neighbours_graph1)
    construct_neighbours_structures(nodes_neighbours_graph1, g)

    clear_graph(g)
    rdf_graph = None

    g = setup_graph(DEFAULT_LOCAL_CONNECTION_STRING)
    rdf_graph = rdflib.Graph()

    node_list_g2 = read_graph_from_rdf_file(input_file2, g, rdf_graph)
    node_list_g2 = sorted(node_list_g2, key=lambda i: i['label'])
    initialize_nodes_neighbours(node_list_g2, node_matrix_mapping_graph2, nodes_neighbours_graph2)
    construct_neighbours_structures(nodes_neighbours_graph2, g)

    similarity_matrix = initialize_similarity_matrix(node_matrix_mapping_graph1, node_matrix_mapping_graph2,
                                                     nodes_neighbours_graph1, nodes_neighbours_graph2, node_list_g1,
                                                     node_list_g2)

    similarity_matrix = apply_similarity_measure(similarity_matrix, node_matrix_mapping_graph1,
                                                 node_matrix_mapping_graph2, nodes_neighbours_graph1,
                                                 nodes_neighbours_graph2, node_list_g1, node_list_g2, 0.1)

    matched_nodes_list = []
    final_similarity_score = get_graph_similarity(similarity_matrix, len(node_matrix_mapping_graph1.keys()),
                                                  len(node_matrix_mapping_graph2.keys()), matched_nodes_list)

    print("Final similarity score between the 2 graphs: " + str(final_similarity_score))

    reasoning = generate_score_explanation(matched_nodes_list, node_matrix_mapping_graph1, node_matrix_mapping_graph2,
                                           nodes_neighbours_graph1, nodes_neighbours_graph2, node_list_g1, node_list_g2)

    clear_graph(g)
    return final_similarity_score, reasoning


def compute_gremlin_match_score(job_description_file, cv_folder_path):
    job_description_text = read_from_txt(job_description_file)
    cv_files_list = [file for file in listdir(cv_folder_path) if isfile(join(cv_folder_path, file))]
    job_description_ttl_file = transform_from_natural_text_to_rdf(job_description_text, "job-description")
    score_list = []
    for cv_file in cv_files_list:

        _, file_extension = os.path.splitext(cv_file)
        if file_extension == ".pdf":
            text = read_cv_entities_from_pdf(cv_folder_path + '/' + cv_file)
        else:
            if file_extension == ".txt":
                text_file = open(cv_folder_path + '/' + cv_file, "r")
                text = text_file.read()
            else:
                text = []
        cv_ttl_file = transform_from_natural_text_to_rdf(text, "cv")
        cv_score, cv_reasoning = gremlin_main(job_description_ttl_file, cv_ttl_file)
        score_list.append((cv_file, cv_score, cv_reasoning))
    return sorted(score_list, key=lambda cv: cv[1], reverse=True)


def read_cv_entities_from_pdf(document_path):
    pdf = pdfplumber.open(document_path)
    text = ""
    for page in pdf.pages:
        text = text + "\n" + page.extract_text()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    return text
