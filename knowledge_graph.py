import igraph
import pandas as pd


def generate_knowledge_graph_components_from_files(vertex_file, edges_file):
    vertex_dataframe = pd.read_csv(vertex_file, header=None)
    edges_dataframe = pd.read_csv(edges_file, header=None)
    vertex_dataframe.rename(columns={0: 'Id',
                                     1: 'Name',
                                     2: 'Label'},
                            inplace=True)
    edges_dataframe.rename(columns={0: 'from',
                                    1: 'to',
                                    2: 'relationship'},
                           inplace=True)
    print(vertex_dataframe)
    print(edges_dataframe)

    graph = igraph.Graph.DataFrame(edges_dataframe.iloc[:, 0:2])
    return vertex_dataframe, graph


def get_shortest_path_between_concepts(from_concept, to_concept, graph, vertex_dataframe):
    from_condition = (vertex_dataframe['Name'] == from_concept)
    to_condition = (vertex_dataframe['Name'] == to_concept)
    from_concept_id = vertex_dataframe[from_condition]['Id']
    to_concept_id = vertex_dataframe[to_condition]['Id']

    if from_concept_id is None or to_concept_id is None:
        return []

    results = graph.get_all_shortest_paths(int(from_concept_id), int(to_concept_id))

    if len(results[0]) > 0:
        # The distance is the number of vertices in the shortest path minus one.
        print("Shortest distance is: ", len(results[0]) - 1)
    else:
        print("End node could not be reached!")
    print(results)
    shortest_paths_list = []
    for path in results:
        name_label_list = []
        for node_id in path:
            name = vertex_dataframe.at[node_id, 'Name']#.astype(str)
            label = vertex_dataframe.at[node_id, 'Label']#.astype(str)
            name_label_list.append((name, label))
        shortest_paths_list.append(name_label_list)
    return shortest_paths_list
