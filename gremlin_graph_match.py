import nest_asyncio
import rdf2g
import re

from rdf2g import setup_graph
from rdf2g import load_rdf2g
from rdf2g import rdflib, expand_tree, get_nodes, clear_graph
import pathlib
from pprint import pprint

COMMON_KEY_LABELS = ['rdfs:comment', 'iri', 'rdfs:label', '@id', '@label', 'amr-core:root', 'amr-core:has-sentence',
                     'amr-core:has-id', 'amr-core:has-date']
COMMON_LABELS_VALUES = 'Role|FrameRole|Frame|AMR|Concept|NamedEntity|Class'  # pentru label ce nu luam in considerare -> match case


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
        print("Label: " + str(label))
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


def get_number_of_neighbours(node_neighbours_graph, iri_node, neighbour_kind):
    node_info_g1 = list(filter(lambda ndi: ndi["iri"] == iri_node, node_neighbours_graph))
    return len(node_info_g1[0][neighbour_kind])


def compute_initial_similarity(iri_node_g1, iri_node_g2, nodes_neighbours_g1, nodes_neighbours_g2, similarity_type):
    neighbours_nr_node_g1 = get_number_of_neighbours(nodes_neighbours_g1, iri_node_g1, similarity_type)
    neighbours_nr_node_g2 = get_number_of_neighbours(nodes_neighbours_g2, iri_node_g2, similarity_type)
    max_in_neighbours = max(neighbours_nr_node_g1, neighbours_nr_node_g2)
    if neighbours_nr_node_g1 == neighbours_nr_node_g2 and neighbours_nr_node_g1 == 0:
        return 1
    if max_in_neighbours == 0:
        return 0
    return min(neighbours_nr_node_g1, neighbours_nr_node_g2) / max_in_neighbours


def initialize_similarity_matrix(node_mapping_g1, node_mapping_g2, nodes_neighbours_g1, nodes_neighbours_g2,
                                 list_node_g1, list_node_g2):
    iri_keys_g1 = node_mapping_g1.keys()
    iri_keys_g2 = node_mapping_g2.keys()
    matrix = [[0 for _ in range(len(iri_keys_g2))] for _ in range(len(iri_keys_g1))]
    for iri_node_g1 in iri_keys_g1:
        for iri_node_g2 in iri_keys_g2:
            in_similarity = compute_initial_similarity(iri_node_g1, iri_node_g2, nodes_neighbours_g1,
                                                       nodes_neighbours_g2, "in-neighbours")
            out_similarity = compute_initial_similarity(iri_node_g1, iri_node_g2, nodes_neighbours_g1,
                                                        nodes_neighbours_g2, "out-neighbours")
            matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] = (in_similarity + out_similarity) / 2
            if (in_similarity + out_similarity) / 2 > 0.0:
                node1 = list(filter(lambda ndi: ndi["iri"][0] == iri_node_g1, list_node_g1))
                node1_info = node1[0]

                node2 = list(filter(lambda ndi: ndi["iri"][0] == iri_node_g2, list_node_g2))
                node2_info = node2[0]

                if 'rdfs:label' in node1_info:
                    if 'rdfs:label' in node2_info:
                        matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] *= (int(
                            node1[0]['label'] == node2[0]['label']) + int(
                            node1[0]['rdfs:label'] == node2[0]['rdfs:label'])) / 2
                    else:
                        matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] *= int(
                            node1[0]['label'] == node2[0]['label']) / 2
                else:
                    matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] *= int(
                        node1[0]['label'] == node2[0]['label'])
    return matrix


def get_best_similarity_score(neighbour_list1, neighbour_list2, node_mapping_list1, node_mapping_list2, matrix, mode):
    similarity_score = 0
    best_choices_dict = {}
    for neighbour_iri in neighbour_list1:
        best_match_score = 0
        best_match_index = -1
        index_neighbour1 = node_mapping_list1[neighbour_iri]
        for neighbour_iri2 in neighbour_list2:
            if neighbour_iri2 not in best_choices_dict:
                if mode == 0:
                    if matrix[index_neighbour1][node_mapping_list2[neighbour_iri2]] > best_match_score:
                        best_match_score = matrix[index_neighbour1][node_mapping_list2[neighbour_iri2]]
                        best_match_index = node_mapping_list2[neighbour_iri2]
                else:
                    if matrix[node_mapping_list2[neighbour_iri2]][index_neighbour1] > best_match_score:
                        best_match_score = matrix[node_mapping_list2[neighbour_iri2]][index_neighbour1]
                        best_match_index = node_mapping_list2[neighbour_iri2]
        best_choices_dict[best_match_index] = best_match_score
    scores_list = list(best_choices_dict.values())
    for score in scores_list:
        similarity_score += score
    return similarity_score


def get_similarity_score_for_neighbours(iri_node_g1, iri_node_g2, node_mapping_g1, node_mapping_g2, nodes_neighbours_g1,
                                        nodes_neighbours_g2, neighbour_type, matrix):
    node_info_g1 = list(filter(lambda ndi: ndi["iri"] == iri_node_g1, nodes_neighbours_g1))
    neighbours_nr_node_g1 = len(node_info_g1[0][neighbour_type])
    node_info_g2 = list(filter(lambda ndi: ndi["iri"] == iri_node_g2, nodes_neighbours_g2))
    neighbours_nr_node_g2 = len(node_info_g2[0][neighbour_type])
    max_neighbours = max(neighbours_nr_node_g1, neighbours_nr_node_g2)
    min_neighbours = min(neighbours_nr_node_g1, neighbours_nr_node_g2)
    if min_neighbours == neighbours_nr_node_g1:
        similarity_score = get_best_similarity_score(node_info_g1[0][neighbour_type], node_info_g2[0][neighbour_type],
                                                     node_mapping_g1, node_mapping_g2, matrix, 0)
    else:
        similarity_score = get_best_similarity_score(node_info_g2[0][neighbour_type], node_info_g1[0][neighbour_type],
                                                     node_mapping_g2, node_mapping_g1, matrix, 1)
    if max_neighbours == 0:
        return 1
    return similarity_score / max_neighbours


def get_nodes_similarity(iri_node_g1, iri_node_g2, list_node_g1, list_node_g2):
    node1 = list(filter(lambda ndi: ndi["iri"][0] == iri_node_g1, list_node_g1))
    node1_info = node1[0]

    node2 = list(filter(lambda ndi: ndi["iri"][0] == iri_node_g2, list_node_g2))
    node2_info = node2[0]
    if 'rdfs:label' in node1_info:
        if 'rdfs:label' in node2_info:
            return (int(node1[0]['label'] == node2[0]['label']) + int(
                node1[0]['rdfs:label'] == node2[0]['rdfs:label'])) / 2
        else:
            return int(node1[0]['label'] == node2[0]['label']) / 2
    return int(node1[0]['label'] == node2[0]['label'])


def apply_similarity_measure(matrix, node_mapping_g1, node_mapping_g2, nodes_neighbours_g1, nodes_neighbours_g2,
                             list_node_g1, list_node_g2, epsilon):
    iri_keys_g1 = node_mapping_g1.keys()
    iri_keys_g2 = node_mapping_g2.keys()
    terminated = False
    iterations = 0
    while not terminated:
        max_difference = 0
        for iri_node_g1 in iri_keys_g1:
            for iri_node_g2 in iri_keys_g2:
                in_similarity_score = get_similarity_score_for_neighbours(iri_node_g1, iri_node_g2, node_mapping_g1,
                                                                          node_mapping_g2, nodes_neighbours_g1,
                                                                          nodes_neighbours_g2, "in-neighbours", matrix)
                out_similarity_score = get_similarity_score_for_neighbours(iri_node_g1, iri_node_g2, node_mapping_g1,
                                                                           node_mapping_g2, nodes_neighbours_g1,
                                                                           nodes_neighbours_g2, "out-neighbours",
                                                                           matrix)
                node_label_similarity = get_nodes_similarity(iri_node_g1, iri_node_g2, list_node_g1, list_node_g2)
                temp_result = (in_similarity_score + out_similarity_score + node_label_similarity) / 3
                max_difference = max(
                    abs(matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] - temp_result),
                    max_difference)
                matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] = temp_result
        if max_difference < epsilon:
            terminated = True
        iterations += 1
    print("Iterations: " + str(iterations))
    return matrix


def get_graph_similarity(matrix, nr_rows, nr_cols, matched_nodes_list):
    taken_nodes = []
    graph_similarity_score = 0.0
    if nr_rows > nr_cols:
        for i in range(0, nr_cols):
            max_score = 0.0
            max_index = -1
            for j in range(0, nr_rows):
                if j not in taken_nodes and matrix[j][i] > max_score:
                    max_score = matrix[j][i]
                    max_index = j
            taken_nodes.append(max_index)
            matched_nodes_list.append((max_index, i, max_score))
            graph_similarity_score += max_score
            print("Added " + str(max_score))
        graph_similarity_score /= nr_cols
    else:
        for i in range(0, nr_rows):
            max_score = 0.0
            max_index = -1
            for j in range(0, nr_cols):
                if j not in taken_nodes and matrix[i][j] > max_score:
                    max_score = matrix[i][j]
                    max_index = j
            taken_nodes.append(max_index)
            matched_nodes_list.append((i, max_index, max_score))
            graph_similarity_score += max_score
            print("Added " + str(max_score))
        graph_similarity_score /= nr_rows
    return graph_similarity_score


def read_graph_from_rdf_file(filename, g, rdf_graph):
    OUTPUT_FILE_LAM_PROPERTIES = pathlib.Path(filename).resolve()

    rdf_graph.parse(str(OUTPUT_FILE_LAM_PROPERTIES), "ttl")
    load_rdf2g(g, rdf_graph)

    # Get Node and neighbours structure Graph
    return get_nodes(g)


def construct_neighbours_structures(nodes_neighbours_graph, g):
    for node_dict_neighbour in nodes_neighbours_graph:
        traversal = g.V().has('iri', node_dict_neighbour['iri']).outE().inV().tree().next()
        nodes_info = expand_tree(g, traversal)
        if nodes_info:
            pprint(nodes_info[0])
            set_in_out_nodes_of_node(nodes_info[0], node_dict_neighbour, nodes_neighbours_graph)


def filter_not_relevant_nodes(node_list, node_mapping):
    not_relevant_nodes_index_list = []
    for node_dict_info in node_list:
        match_list = re.findall(COMMON_LABELS_VALUES, node_dict_info['label'])
        if any(match_list):
            node_index = node_mapping[node_dict_info['iri'][0]]
            not_relevant_nodes_index_list.append(node_index)
    return not_relevant_nodes_index_list


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


def get_feedback(matched_nodes_list, node_mapping_g1, node_mapping_g2,
                 nodes_neighbours_g1, nodes_neighbours_g2, node_list_g1, node_list_g2):
    taken_nodes = []
    feedback_list = []
    not_relevant_nodes_index_list_g1 = filter_not_relevant_nodes(node_list_g1, node_mapping_g1)
    not_relevant_nodes_index_list_g2 = filter_not_relevant_nodes(node_list_g2, node_mapping_g2)

    relevant_matched_tuple = []
    for matched_tuple in matched_nodes_list:
        if (matched_tuple[0] not in not_relevant_nodes_index_list_g1) and (
                matched_tuple[1] not in not_relevant_nodes_index_list_g2):
            relevant_matched_tuple.append(matched_tuple)

    relevant_matched_tuple.sort(key=lambda mt: mt[2], reverse=True)
    best_5_relevant_matches_list = relevant_matched_tuple[0:11]
    for best_matched_tuple in best_5_relevant_matches_list:
        # node1 = list(filter(lambda nm: nm.values()[0] == best_matched_tuple[0], node_mapping_g1))
        iri_list_g1 = list(node_mapping_g1.keys())
        index_list_g1 = list(node_mapping_g1.values())
        node1_iri = iri_list_g1[index_list_g1.index(best_matched_tuple[0])]

        # node2 = list(filter(lambda nm: nm.values()[0] == best_matched_tuple[1], node_mapping_g2))
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

    print("-----SIMILARITY--MATRIX--INITIAL-----")
    for line in similarity_matrix:
        print('  '.join(map(str, line)))

    similarity_matrix = apply_similarity_measure(similarity_matrix, node_matrix_mapping_graph1,
                                                 node_matrix_mapping_graph2, nodes_neighbours_graph1,
                                                 nodes_neighbours_graph2, node_list_g1, node_list_g2, 0.1)

    print("-----SIMILARITY--MATRIX--FINAL-----")

    for line in similarity_matrix:
        print('  '.join(map(str, line)))

    matched_nodes_list = []
    final_similarity_score = get_graph_similarity(similarity_matrix, len(node_matrix_mapping_graph1.keys()),
                                                  len(node_matrix_mapping_graph2.keys()), matched_nodes_list)

    print("Final similarity score between the 2 graphs: " + str(final_similarity_score))

    print("-----Node--Mapping--G1")
    pprint(node_matrix_mapping_graph1)

    print("-----Node--Mapping--G2")
    pprint(node_matrix_mapping_graph2)

    pprint(get_feedback(matched_nodes_list,
                        node_matrix_mapping_graph1, node_matrix_mapping_graph2, nodes_neighbours_graph1,
                        nodes_neighbours_graph2, node_list_g1, node_list_g2))

    clear_graph(g)


if __name__ == "__main__":
    gremlin_main("past-temporal-demo-amr.ttl", "past-temporal-demo-amr-ex2.ttl")
