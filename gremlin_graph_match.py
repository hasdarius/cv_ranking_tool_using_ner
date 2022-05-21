import nest_asyncio
import rdf2g



from rdf2g import setup_graph
from rdf2g import load_rdf2g
from rdf2g import rdflib, expand_tree, get_nodes, clear_graph
import pathlib
from pprint import pprint

COMMON_KEY_LABELS = ['rdfs:comment', 'iri', 'rdfs:label', '@id', '@label', 'amr-core:root', 'amr-core:has-sentence',
                     'amr-core:has-id', 'amr-core:has-date']


def initialize_nodes_neighbours(node_list, node_matrix_mapping, nodes_neighbours):
    # node_list = get_nodes(graph)
    iter = 0
    for dict_node in node_list:
        nodes_neighbours.append({"iri": dict_node['iri'][0], "in-neighbours": [], "out-neighbours": []})
        node_matrix_mapping[dict_node['iri'][0]] = iter
        iter += 1


def set_in_out_nodes_of_node(node, node_dict_info, nodes_neighbours):
    out_nodes_list = []
    # print(node)
    for label in node.keys():
        if label not in COMMON_KEY_LABELS:
            out_nodes_list.append(node[label])
            if not isinstance(node[label], str):
                node_dict_info["out-neighbours"].append(node[label]['iri'])
                neighbour = list(filter(lambda ndi: ndi["iri"] == node[label]['iri'], nodes_neighbours))
                # if neighbour:
                neighbour[0]["in-neighbours"].append(node['iri'])
            # else:
            #     nodes_neighbours_graph1.append({"iri": node[label]['iri'], "in-neighbours": [node['iri']], "out-neighbours": []})
    # print(out_nodes_list)


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
            # print(iri_node_g1)
            # print(iri_node_g2)
            # print(node_mapping_g1[iri_node_g1])
            # print(node_mapping_g2[iri_node_g2])
            # print((in_similarity + out_similarity)/2)
            # print("----------------------------------------------------------")
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
                # print(neighbour_iri2)
                # print("Index1: " + str(index_neighbour1) + " Index 2: " + str(node_mapping_list2[neighbour_iri2]))
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
                # if temp_result > 1:
                #     print("In value: " + str(in_similarity_score) + " Out value: " + str(out_similarity_score) + " Label value: " + str(node_label_similarity))
                max_difference = max(
                    abs(matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] - temp_result),
                    max_difference)
                matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] = temp_result
        if max_difference < epsilon:
            terminated = True
        iterations += 1
    print("Iterations: " + str(iterations))
    return matrix


def get_graph_similarity(matrix, nr_rows, nr_cols):
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
            graph_similarity_score += max_score
            print("Added " + str(max_score))
        graph_similarity_score /= nr_rows
    return graph_similarity_score


def read_graph_from_rdf_file(filename, g, rdf_graph):
    # filename = "past-temporal-demo-amr"
    OUTPUT_FILE_LAM_PROPERTIES = pathlib.Path(filename + ".ttl").resolve()

    rdf_graph.parse(str(OUTPUT_FILE_LAM_PROPERTIES), "ttl")
    load_rdf2g(g, rdf_graph)

    # Get Node and neighbours structure Graph1
    return get_nodes(g)


def construct_neighbours_structures(nodes_neighbours_graph, g):
    for node_dict_neighbour in nodes_neighbours_graph:
        # print(node_dict_neighbour['iri'])
        # print(g)
        traversal = g.V().has('iri', node_dict_neighbour['iri']).outE().inV().tree().next()
        # print(traversal)
        nodes_info = expand_tree(g, traversal)
        if nodes_info:
            set_in_out_nodes_of_node(nodes_info[0], node_dict_neighbour, nodes_neighbours_graph)


def main(input_file1, input_file2):
    nodes_neighbours_graph1 = []
    nodes_neighbours_graph2 = []
    node_matrix_mapping_graph1 = {}
    node_matrix_mapping_graph2 = {}

    DEFAULT_LOCAL_CONNECTION_STRING = "ws://localhost:8182/gremlin"
    g = setup_graph(DEFAULT_LOCAL_CONNECTION_STRING)
    rdf_graph = rdflib.Graph()

    node_list_g1 = read_graph_from_rdf_file(input_file1, g, rdf_graph)
    node_list_g1 = sorted(node_list_g1, key=lambda i: i['label'])
    #s = g.V().has('iri', "http://amr.isi.edu/rdf/amr-terms#temporal-quantity").outE().inV().tree().next()
    #result = rdf2g.expand_tree(g, s)
    #pprint(result)

    initialize_nodes_neighbours(node_list_g1, node_matrix_mapping_graph1, nodes_neighbours_graph1)
    #pprint(nodes_neighbours_graph1)
    construct_neighbours_structures(nodes_neighbours_graph1, g)

    clear_graph(g)
    rdf_graph = None

    g = setup_graph(DEFAULT_LOCAL_CONNECTION_STRING)
    rdf_graph = rdflib.Graph()

    node_list_g2 = read_graph_from_rdf_file(input_file2, g, rdf_graph)
    node_list_g2 = sorted(node_list_g2, key=lambda i: i['label'])
    initialize_nodes_neighbours(node_list_g2, node_matrix_mapping_graph2, nodes_neighbours_graph2)
    construct_neighbours_structures(nodes_neighbours_graph2, g)

    # pprint(nodes_neighbours_graph1)
    # print("--------GRAPH2--------")
    # pprint(nodes_neighbours_graph2)

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

    final_similarity_score = get_graph_similarity(similarity_matrix, len(node_matrix_mapping_graph1.keys()),
                                                  len(node_matrix_mapping_graph2.keys()))

    print("Final similarity score between the 2 graphs: " + str(final_similarity_score))

    print("-----Node--Mapping--G1")
    pprint(node_matrix_mapping_graph1)

    print("-----Node--Mapping--G2")
    pprint(node_matrix_mapping_graph2)
    clear_graph(g)


JOB_DESCRIPTION_EXAMPLE = """Skills

Must have

- Mandatory Computer Science Faculty / Cybernetics / Mathematics / Informatics graduated
- Min 1 Year working hands on experience in Java
- Java 8
- Dependency Injection/ Inversion of Control (Spring or JBoss)
- Unit and Mock Testing (JUnit, Mockito, Arquillian, Cucumber)
- Java Message Service (JMS)
- Web Services (JAX-RS, JAX-WS)
- Strong understanding of Design and Architectural Patterns
- Apache Maven
- Continuous Integration tools (Jenkins or similar)
- Linux operating system
- Stash: GIT Repository Management
- Spoken English language is a must

Nice to have

- Apache Camel
- Enterprise Integration Patterns
- Java Architecture for XML Binding (JAXB)
- XML Transformations (XSLT, XSD, DTD)
- FitNesse
- Drools
- Agile Methodologies (SCRUM and Kanban)
- Additional knowledge of financial products is a plus

Languages

Romanian: C2 Proficient

English: C1 Advanced

Seniority

Junior"""

if __name__ == "__main__":
    nest_asyncio.apply()
    main("past-temporal-demo-amr", "past-temporal-demo-amr-ex2")
