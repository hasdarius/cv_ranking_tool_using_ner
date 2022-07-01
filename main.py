import shutil
import sys
import os.path as path
from pprint import pprint
import time

from ner import train_custom_ner
from ner.cv_scorer import rank_cvs
from nlp_scorer.gremlin_graph_scorer import compute_gremlin_match_score

from utilities.constants import *

if __name__ == "__main__":
    start = time.time()
    args = sys.argv[1:]
    option = args[0]
    if option == 'train':
        if path.exists(train_custom_ner.CUSTOM_SPACY_MODEL):
            shutil.rmtree(train_custom_ner.CUSTOM_SPACY_MODEL)
        training_data = train_custom_ner.csv_to_spacy_format('Data/train.csv', '-')
        train_custom_ner.fine_tune_and_save_custom_model(training_data,
                                                         new_model_name='technology_it_model',
                                                         output_dir=train_custom_ner.CUSTOM_SPACY_MODEL)
    else:
        if option == 'score':
            if not path.exists(train_custom_ner.CUSTOM_SPACY_MODEL):
                print('A model does not exist. Before scoring, you need to train a model')
            else:
                score_list_ner = rank_cvs(JOB_DESCRIPTION_1_PATH, CV_DIRECTORY)
                score_list_gremlin = compute_gremlin_match_score(JOB_DESCRIPTION_1_PATH, CV_DIRECTORY)

                final_result_list = []
                for cv_result_ner in score_list_ner:
                    cv_result_gremlin = list(
                        filter(lambda cv_tuple: cv_tuple[0] == cv_result_ner[0], score_list_gremlin))
                    final_result_list.append(
                        (cv_result_ner[0], float(((100 * cv_result_gremlin[0][1]) + 100 * cv_result_ner[1]) / 2),
                         cv_result_ner[2] + cv_result_gremlin[0][2]))

                end = time.time()
                elapsed_time = end - start
                print('Execution time:', elapsed_time, 'seconds')
                pprint(sorted(final_result_list, key=lambda resume: resume[1], reverse=True))
        else:
            print("The only available option when running the tool are 'train' and 'score'")


