import shutil
import sys
import os.path as path
from pprint import pprint
import time

from ner import train_custom_ner
from ner.cv_scorer import rank_cvs
from nlp_scorer.gremlin_graph_scorer import compute_gremlin_match_score

from utilities.constants import CV_DIRECTORY

JOB_DESCRIPTION_EXAMPLE = """
Looking for a mid software developer.
Skills in:
- Java for 3+ years or other similar programming languages: Scala, Kotlin.
- Open and willing to learn new technologies
- Strong Java Core, Spring Boot knowledge
- Experience with tools like jUnit, Maven and Jenkins
- Good understanding of design patterns
- Developed REST API's using Spring Boot
- Bachelor Degree in Computer Science"""

JOB_DESCRIPTION_EXAMPLE2 = """Main requirements: 
- Java development experience 3+ years 
- Open and willing to learn new technologies
- Strong Java Core knowledge
- Good understanding of design patterns """


JOB_DESCRIPTION_EXAMPLE3 = """Requirements: 2 years of experience in JavaScript."""


JOB_DESCRIPTION_EXAMPLE4 = """Skills

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
                score_list_ner = rank_cvs(JOB_DESCRIPTION_EXAMPLE, CV_DIRECTORY)
                score_list_gremlin = compute_gremlin_match_score(JOB_DESCRIPTION_EXAMPLE3, CV_DIRECTORY)

                final_result_list = []
                for cv_result_ner in score_list_ner:
                    cv_result_gremlin = list(
                        filter(lambda cv_tuple: cv_tuple[0] == cv_result_ner[0], score_list_gremlin))
                    final_result_list.append(
                        (cv_result_ner[0], float(((100 * cv_result_gremlin[0][1]) + cv_result_ner[1]) / 2),
                         cv_result_ner[2] + cv_result_gremlin[0][2]))

                end = time.time()
                elapsed_time = end - start
                print('Execution time:', elapsed_time, 'seconds')
                pprint(final_result_list)
        else:
            print("The only available option when running the tool are 'train' and 'score'")


