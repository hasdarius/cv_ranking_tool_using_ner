import os
from os import listdir
from os.path import isfile, join

import amrlib

from datetime import datetime
from pathlib import Path

from constants import TXT_FILES_DIRECTORY, TTL_FILES_DIRECTORY
from gremlin_graph_match import gremlin_main


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
        #print(graph)
        f.write(graph)
    f.close()

    os.system("python ./utils/amr-ld/amr_to_rdf.py -i " + txt_file_path + " -o " + ttl_file_path + " -f ttl")
    return ttl_file_path


def compute_gremlin_match_score(job_description_text, cv_files, cv_folder):
    job_description_ttl_file = transform_from_natural_text_to_rdf(job_description_text, "job-description")
    score_list = []
    for cv_file in cv_files:
        text_file = open(cv_folder + '/' + cv_file, "r")
        text = text_file.read()
        cv_ttl_file = transform_from_natural_text_to_rdf(text, "cv")
        cv_score = gremlin_main(job_description_ttl_file, cv_ttl_file)
        score_list.append((cv_file, cv_score))
    return score_list


JOB_DESCRIPTION_EXAMPLE = """Looking for a Software Developer with at least one year of experience in Java 8, 
it would be nice to have experience in Spring Boot, Gradle, you must have a bachelor degree in Computer Science or 
Mathematics or Economics. """

if __name__ == "__main__":
    cv_folder_path = "./utils/cv_directory"
    cv_files_list = [file for file in listdir(cv_folder_path) if isfile(join(cv_folder_path, file))]
    compute_gremlin_match_score(JOB_DESCRIPTION_EXAMPLE, cv_files_list, cv_folder_path)

#
#
common_labels = {"Role", "FrameRole", "Frame", "AMR", "Concept", "NamedEntity", "Class"}  # pentru label ce nu luam in considerare -> match case
# la label -> ce luam in considerare propbank(verbe) sau entity type, amr-terms sau amr-core
# la rdfs label sa nu contina AMR -> lista[0]