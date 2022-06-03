from pyspark.sql import SparkSession
from graphframes import GraphFrame


def generate_knowledge_graph_components_from_files(vertex_file, edges_file):
    spark = SparkSession.builder.appName(
        'KnowledgeGraph').getOrCreate()

    vertices = spark.read.csv(vertex_file, sep=',',
                              inferSchema=True, header=False) \
        .withColumnRenamed("_1", "id").withColumnRenamed("_2", "instance").withColumnRenamed("_3", "label")
    edges = spark.read.csv(edges_file, sep=',',
                           inferSchema=True, header=False) \
        .withColumnRenamed("_1", "src").withColumnRenamed("_2", "dest").withColumnRenamed("_3", "relationship")

    graph = GraphFrame(vertices, edges)
    graph.vertices.show()
    graph.edges.show()

    return graph
