import sys
import time

from ner.cv_scorer import rank_cvs
from ner.train_custom_ner import *
from nlp_scorer.gremlin_graph_scorer import compute_gremlin_match_score
from utilities.constants import *
from utilities.file_util import write_tuple_list_to_csv


def main(job_description_file, cv_directory):
    start = time.time()
    args = sys.argv[1:]
    option = args[0]
    if option == 'train':
        begin_training()
    else:
        if option == 'score':
            if not os.path.exists(CUSTOM_SPACY_MODEL):
                print('A model does not exist. Before scoring, you need to train a model')
            else:
                score_list_ner = rank_cvs(job_description_file, cv_directory)
                score_list_gremlin = compute_gremlin_match_score(job_description_file, cv_directory)

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

                write_tuple_list_to_csv(final_result_list, "results_" + os.path.basename(job_description_file) + ".csv")
        else:
            print("The only available option when running the application are 'train' and 'score'")


if __name__ == "__main__":
    main(JOB_DESCRIPTION_1_PATH, CV_DIRECTORY)

