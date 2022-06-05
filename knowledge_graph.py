import pandas as pd
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib import pylab


def generate_knowledge_graph_components_from_files(edges_file):
    edges = pd.read_csv(edges_file, header=None)
    edges.columns = ['from', 'relationship', 'to']

    graph = nx.from_pandas_edgelist(edges, 'from', 'to', 'relationship', create_using=nx.DiGraph)

    programming_languages = [(fromVertex, toVertex, relationship) for fromVertex, toVertex, relationship in graph.edges(data=True) if
                             relationship['relationship'] == 'isA' and toVertex == 'Programming Language']
    # get all programming languages from knowledge graph
    return graph


def get_shortest_path_between_concepts(from_concept, to_concept, graph):
    if not nx.has_path(graph, from_concept, to_concept):
        return []
    results = list(nx.shortest_path(graph, from_concept, to_concept))
    shortest_path_length = len(results) - 1

    if shortest_path_length > 0:
        # The distance is the number of vertices in the shortest path minus one.
        print("Shortest distance is: ", shortest_path_length)
    else:
        print("End node could not be reached!")
    return results, shortest_path_length


def print_graph(graph):
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    pos = nx.spring_layout(graph)
    edge_labels = nx.get_edge_attributes(graph, 'relationship')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels)
    nx.draw(graph, with_labels=True)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)
    plt.savefig('knowledgeGraph.png', bbox_inches="tight")
    pylab.close()
    plt.show()
