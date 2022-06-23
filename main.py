import time
from os import path
from pprint import pprint

from ner import train_custom_ner
from ner.cv_scorer import rank_cvs
from nlp_scorer.gremlin_graph_scorer import compute_gremlin_match_score
from utilities.constants import CV_DIRECTORY

JOB_DESCRIPTION_EXAMPLE2 = """Main requirements: 
- Java development experience 3+ years 
- Open and willing to learn new technologies
- Strong Java Core knowledge
- Good understanding of design patterns """


def main(input_file):
    start = time.time()
    if not path.exists(train_custom_ner.CUSTOM_SPACY_MODEL):
        json_file_name = train_custom_ner.csv_to_json_with_labels(input_file, '-')
        training_data = train_custom_ner.json_to_spacy_format(json_file_name)
        train_custom_ner.fine_tune_and_save_custom_model(training_data,
                                                         new_model_name='technology_it_model',
                                                         output_dir=train_custom_ner.CUSTOM_SPACY_MODEL)
    score_list_ner = rank_cvs(JOB_DESCRIPTION_EXAMPLE2, CV_DIRECTORY)
    score_list_gremlin = compute_gremlin_match_score(JOB_DESCRIPTION_EXAMPLE2, CV_DIRECTORY)

    final_result_list = []
    for cv_result_ner in score_list_ner:
        cv_result_gremlin = list(filter(lambda cv_tuple: cv_tuple[0] == cv_result_ner[0], score_list_gremlin))
        final_result_list.append((cv_result_ner[0], float((cv_result_gremlin[0][1] + cv_result_ner[1]) / 2),
                                  cv_result_ner[2] + cv_result_gremlin[0][2]))

    end = time.time()
    pprint(final_result_list)
    elapsed_time = end - start
    print('Execution time:', elapsed_time, 'seconds')

JOB_DESCRIPTION_EXAMPLE = """Skills

Must have

- Mandatory Computer Science Faculty / Cybernetics / Mathematics / Informatics graduated
- Min 1 Year working hands on experience in Object oriented, Scala, Ruby
- Dependency Injection/ Inversion of Control (Spring or JBoss)
- Unit and Mock Testing (JUnit, Mockito, Arquillian, Cucumber)
- Message Service (JMS)
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
- Architecture for XML Binding (JAXB)
- XML Transformations (XSLT, XSD, DTD)
- FitNesse
- Drools
- Agile Methodologies (SCRUM and Kanban)
- Additional knowledge of financial products is a plus

Languages

Romanian: C2 Proficient

English: C1 Advanced

OCA certificate

Seniority

Junior"""

if __name__ == "__main__":
    main("Data/train.csv")
