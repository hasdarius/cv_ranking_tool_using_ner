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


def compute_initial_similarity(iri_node_g1, iri_node_g2, nodes_neighbours_g1, nodes_neighbours_g2, similarity_type):
    neighbours_nr_node_g1 = get_number_of_neighbours(nodes_neighbours_g1, iri_node_g1, similarity_type)
    neighbours_nr_node_g2 = get_number_of_neighbours(nodes_neighbours_g2, iri_node_g2, similarity_type)
    max_in_neighbours = max(neighbours_nr_node_g1, neighbours_nr_node_g2)
    if neighbours_nr_node_g1 == neighbours_nr_node_g2 and neighbours_nr_node_g1 == 0:
        return 1
    if max_in_neighbours == 0:
        return 0
    return min(neighbours_nr_node_g1, neighbours_nr_node_g2) / max_in_neighbours


def get_number_of_neighbours(node_neighbours_graph, iri_node, neighbour_kind):
    node_info_g1 = list(filter(lambda ndi: ndi["iri"] == iri_node, node_neighbours_graph))
    return len(node_info_g1[0][neighbour_kind])


def apply_similarity_measure(matrix, node_mapping_g1, node_mapping_g2, nodes_neighbours_g1, nodes_neighbours_g2,
                             list_node_g1, list_node_g2, epsilon):
    iri_keys_g1 = node_mapping_g1.keys()
    iri_keys_g2 = node_mapping_g2.keys()
    terminated = False
    iterations = 0
    while not terminated:
        max_difference = -1
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
                temp_result = round((in_similarity_score + out_similarity_score + node_label_similarity) / 3, 10)
                max_difference = max(
                    abs(matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] - temp_result),
                    max_difference)
                matrix[node_mapping_g1[iri_node_g1]][node_mapping_g2[iri_node_g2]] = temp_result
        if max_difference < epsilon:
            terminated = True
        iterations += 1
    print("Iterations: " + str(iterations))
    return matrix


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


def get_best_similarity_score(neighbour_list1, neighbour_list2, node_mapping_list1, node_mapping_list2, matrix, mode):
    similarity_score = 0
    best_choices_dict = {}
    neighbour_list1 = sorted(neighbour_list1)
    neighbour_list2 = sorted(neighbour_list2)
    for neighbour_iri in neighbour_list1:
        best_match_score = -1
        best_match_index = -1
        index_neighbour1 = node_mapping_list1[neighbour_iri]
        for neighbour_iri2 in neighbour_list2:
            index_neighbour2 = node_mapping_list2[neighbour_iri2]
            if index_neighbour2 not in best_choices_dict:
                if mode == 0:
                    if matrix[index_neighbour1][index_neighbour2] > best_match_score:
                        best_match_score = matrix[index_neighbour1][index_neighbour2]
                        best_match_index = index_neighbour2
                else:
                    if matrix[index_neighbour2][index_neighbour1] > best_match_score:
                        best_match_score = matrix[index_neighbour2][index_neighbour1]
                        best_match_index = index_neighbour2
        best_choices_dict[best_match_index] = best_match_score
    scores_list = list(best_choices_dict.values())
    for score in scores_list:
        similarity_score += score
    return similarity_score


def get_nodes_similarity(iri_node_g1, iri_node_g2, list_node_g1, list_node_g2):
    node1 = list(filter(lambda ndi: ndi["iri"][0] == iri_node_g1, list_node_g1))
    node1_information = node1[0]

    node2 = list(filter(lambda ndi: ndi["iri"][0] == iri_node_g2, list_node_g2))
    node2_information = node2[0]
    if 'rdfs:label' in node1_information:
        if 'rdfs:label' in node2_information:
            return (int(node1[0]['label'] == node2[0]['label']) + int(
                node1[0]['rdfs:label'] == node2[0]['rdfs:label'])) / 2
        else:
            return int(node1[0]['label'] == node2[0]['label']) / 2
    return int(node1[0]['label'] == node2[0]['label'])


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
            # print("Added " + str(max_score))
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
            # print("Added " + str(max_score))
        graph_similarity_score /= nr_rows
    return graph_similarity_score
