import os

import amrlib
import pathlib

from datetime import datetime
from pathlib import Path

from rdf2g import load_rdf2g, get_nodes

from utilities.constants import TXT_FILES_DIRECTORY, TTL_FILES_DIRECTORY


def transform_from_natural_text_to_rdf(cv_input_text, file_type):
    stog = amrlib.load_stog_model()
    graphs = stog.parse_sents([cv_input_text])

    Path(TXT_FILES_DIRECTORY).mkdir(parents=True, exist_ok=True)
    Path(TTL_FILES_DIRECTORY).mkdir(parents=True, exist_ok=True)

    dt_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f")
    txt_filename = file_type + "-amr-" + dt_string + ".txt"
    txt_file_path = TXT_FILES_DIRECTORY + "/" + txt_filename
    ttl_filename = file_type + "-amr-" + dt_string + ".ttl"
    ttl_file_path = TTL_FILES_DIRECTORY + "/" + ttl_filename

    f = open(txt_file_path, "w+")
    f.write("# ::id " + txt_filename + " ::date " + dt_string + "\n")
    for graph in graphs:
        # print(graph)
        f.write(graph)
    f.close()

    os.system("python ./utils/amr-ld/amr_to_rdf.py -i " + txt_file_path + " -o " + ttl_file_path + " -f ttl")
    return ttl_file_path


def read_graph_from_rdf_file(filename, g, rdf_graph):
    OUTPUT_FILE_LAM_PROPERTIES = pathlib.Path(filename).resolve()

    rdf_graph.parse(str(OUTPUT_FILE_LAM_PROPERTIES), "ttl")
    load_rdf2g(g, rdf_graph)

    return get_nodes(g)


common_labels = {"Role", "FrameRole", "Frame", "AMR", "Concept", "NamedEntity",
                 "Class"}  # pentru label ce nu luam in considerare -> match case
# la label -> ce luam in considerare propbank(verbe) sau entity type, amr-terms sau amr-core
# la rdfs label sa nu contina AMR -> lista[0]
