import re
from pprint import pprint

COMMON_LABELS_VALUES = 'Role|FrameRole|Frame|AMR|Concept|NamedEntity|Class'  # pentru label ce nu luam in considerare -> match case
COMMON_NEIGHBOURS_IRI = ['http://amr.isi.edu/rdf/core-amr#AMR', 'http://amr.isi.edu/rdf/core-amr#Role']


def generate_score_explanation(matched_nodes_list, node_mapping_g1, node_mapping_g2,
                               nodes_neighbours_g1, nodes_neighbours_g2, node_list_g1, node_list_g2):
    feedback_list = []
    relevant_matched_tuple = get_relevant_matches(matched_nodes_list, node_list_g1, node_list_g2, node_mapping_g1,
                                                  node_mapping_g2, nodes_neighbours_g1, nodes_neighbours_g2)
    for best_matched_tuple in relevant_matched_tuple:
        iri_list_g1 = list(node_mapping_g1.keys())
        index_list_g1 = list(node_mapping_g1.values())
        node1_iri = iri_list_g1[index_list_g1.index(best_matched_tuple[0])]

        iri_list_g2 = list(node_mapping_g2.keys())
        index_list_g2 = list(node_mapping_g2.values())
        node2_iri = iri_list_g2[index_list_g2.index(best_matched_tuple[1])]  # node2[0].keys()[0]

        node1_info = list(filter(lambda ndi: ndi["iri"][0] == node1_iri, node_list_g1))

        node2_info = list(filter(lambda ndi: ndi["iri"][0] == node2_iri, node_list_g2))

        message = get_feedback_message(node1_info, node1_iri, node2_info, node2_iri, node_list_g1, node_list_g2,
                                       nodes_neighbours_g1, nodes_neighbours_g2)
        if message:
            feedback_list.append(message)

    print("The result obtained for the given CV and job description is due to the following reasons listed below:")
    pprint(feedback_list)
    return feedback_list


def get_relevant_matches(matched_nodes_list, node_list_g1, node_list_g2, node_mapping_g1, node_mapping_g2,
                         nodes_neighbours_g1, nodes_neighbours_g2):
    not_relevant_nodes_index_list_g1 = filter_not_relevant_nodes(node_list_g1, node_mapping_g1, nodes_neighbours_g1)
    not_relevant_nodes_index_list_g2 = filter_not_relevant_nodes(node_list_g2, node_mapping_g2, nodes_neighbours_g2)
    relevant_matched_tuple = []
    for matched_tuple in matched_nodes_list:
        if (matched_tuple[0] not in not_relevant_nodes_index_list_g1) and (
                matched_tuple[1] not in not_relevant_nodes_index_list_g2):
            relevant_matched_tuple.append(matched_tuple)
    relevant_matched_tuple.sort(key=lambda mt: mt[2], reverse=True)
    # best_5_relevant_matches_list = relevant_matched_tuple[0:11]
    return relevant_matched_tuple


def filter_not_relevant_nodes(node_list, node_mapping, nodes_neighbours):
    not_relevant_nodes_index_list = []
    for node_dict_info in node_list:
        match_list = re.findall(COMMON_LABELS_VALUES, node_dict_info['label'])
        node_index = node_mapping[node_dict_info['iri'][0]]
        if any(match_list):
            not_relevant_nodes_index_list.append(node_index)
        else:
            node_iri = node_dict_info['iri'][0]
            node_neighbours_of_node = list(filter(lambda ndi: ndi['iri'] == node_iri, nodes_neighbours))
            for not_relevant_out_neighbour_iri in COMMON_NEIGHBOURS_IRI:
                if not_relevant_out_neighbour_iri in node_neighbours_of_node[0]['out-neighbours']:
                    not_relevant_nodes_index_list.append(node_index)
    return not_relevant_nodes_index_list


def get_feedback_message(node1_info, node1_iri, node2_info, node2_iri, node_list_g1, node_list_g2,
                         nodes_neighbours_g1, nodes_neighbours_g2):
    if 'rdfs:label' in node1_info[0] and 'rdfs:label' in node2_info[0]:
        node1_type_label = get_node_type_label(node1_iri, node_list_g1, nodes_neighbours_g1)
        node2_type_label = get_node_type_label(node2_iri, node_list_g2, nodes_neighbours_g2)
        special_term1 = node1_info[0]['rdfs:label']
        special_term2 = node2_info[0]['rdfs:label']
        return str("The Job description text mentions the term: <<" + special_term1[0] + ">> which is "
                                                                                         "identified of "
                                                                                         "having "
                                                                                         "the following "
                                                                                         "type: "
                                                                                         "<<" +
                   node1_type_label + ">> and the CV text mentions the term: <<" + special_term2[
                       0] + ">> which "
                            "is "
                            "identified of having the following type: <<" + node2_type_label + ">>.")
    else:
        node1_label = node1_info[0]['label']
        node2_label = node2_info[0]['label']
        if ('amr-terms' in node1_label) and ('amr-terms' in node2_label):
            term1 = node1_label.replace("amr-terms:", "")
            term2 = node2_label.replace("amr-terms:", "")
            return str("The Job description text references the term: <<" + term1 + ">> and the CV "
                                                                                    "references the"
                                                                                    " following "
                                                                                    "term: <<" +
                       term2 + ">>.")
        elif ('propbank' in node1_label) and ('propbank' in node2_label):
            if ('ARG' not in node1_label) and ('ARG' not in node2_label):
                verb1 = node1_label.replace("propbank:", "")
                verb2 = node2_label.replace("propbank:", "")
                verb1 = re.sub("\-\d+", '', verb1)
                verb2 = re.sub("\-\d+", '', verb2)
                return str("The Job description text references the verb: <<" + verb1 + ">> and the CV "
                                                                                        "references the"
                                                                                        " following "
                                                                                        "verb: <<" +
                           verb2 + ">>.")
    return ""


def get_node_type_label(node1_iri, node_list_g1, nodes_neighbours_g1):
    node_neighbours_of_node1 = list(filter(lambda ndi: ndi['iri'] == node1_iri, nodes_neighbours_g1))
    word1_type_iri = node_neighbours_of_node1[0]['out-neighbours'][0]
    word1_type_info = list(filter(lambda ndi: ndi["iri"][0] == word1_type_iri, node_list_g1))
    return word1_type_info[0]['label'].replace("entity-types:", "")


def get_best_matched_node_info(matched_nodes_list, node_mapping_g1, node_mapping_g2,
                               nodes_neighbours_g1, nodes_neighbours_g2, node_list_g1, node_list_g2):
    feedback_list = []
    relevant_matched_tuple = get_relevant_matches(matched_nodes_list, node_list_g1, node_list_g2, node_mapping_g1,
                                                  node_mapping_g2, nodes_neighbours_g1, nodes_neighbours_g2)

    best_matches_list_size = int(len(relevant_matched_tuple) / 2 + 1)
    best_10_relevant_matches_list = relevant_matched_tuple[0:best_matches_list_size]
    for best_matched_tuple in best_10_relevant_matches_list:
        iri_list_g1 = list(node_mapping_g1.keys())
        index_list_g1 = list(node_mapping_g1.values())
        node1_iri = iri_list_g1[index_list_g1.index(best_matched_tuple[0])]

        iri_list_g2 = list(node_mapping_g2.keys())
        index_list_g2 = list(node_mapping_g2.values())
        node2_iri = iri_list_g2[index_list_g2.index(best_matched_tuple[1])]  # node2[0].keys()[0]

        node1_info = list(filter(lambda ndi: ndi["iri"][0] == node1_iri, node_list_g1))
        node1_label = node1_info[0]['label']

        node2_info = list(filter(lambda ndi: ndi["iri"][0] == node2_iri, node_list_g2))
        node2_label = node2_info[0]['label']

        node1_neighbour_labels = get_neighbour_labels(node1_iri, node_list_g1, nodes_neighbours_g1)
        node2_neighbour_labels = get_neighbour_labels(node2_iri, node_list_g2, nodes_neighbours_g2)

        feedback_list.append(
            {"node-from-G1-label": node1_label, "neighbours-labels-of-node-from-G1": node1_neighbour_labels,
             "node-from-G2-label": node2_label, "neighbours-labels-of-node-from-G2": node2_neighbour_labels})

    return feedback_list


def get_neighbour_labels(node_iri, node_list, nodes_neighbours):
    node_neighbour_labels = []
    node_neighbours_of_node = list(filter(lambda ndi: ndi['iri'] == node_iri, nodes_neighbours))
    # print("------NODES----NEIGHBOURS")
    # pprint(node_neighbours_of_node)
    node_in_neighbours = node_neighbours_of_node[0]['in-neighbours']
    for neighbour in node_in_neighbours:
        neighbour_info = list(filter(lambda ndi: ndi["iri"][0] == neighbour, node_list))
        node_neighbour_labels.append(neighbour_info[0]['label'])
    node_out_neighbours = node_neighbours_of_node[0]['out-neighbours']
    for neighbour in node_out_neighbours:
        neighbour_info = list(filter(lambda ndi: ndi["iri"][0] == neighbour, node_list))
        node_neighbour_labels.append(neighbour_info[0]['label'])
    return node_neighbour_labels
