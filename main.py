import shutil
import sys
import os.path as path
from pprint import pprint

import train_custom_ner
from cv_scorer import rank_cvs

# JOB_DESCRIPTION_EXAMPLE = """Skills
#
# Must have
#
# - Mandatory Computer Science Faculty / Cybernetics / Mathematics / Informatics graduated
# - Min 1 Year working hands on experience in Object oriented with Programming Languages such as Java, Scala and Ruby
# - Dependency Injection/ Inversion of Control (Spring or JBoss)
# - Unit and Mock Testing (JUnit, Mockito, Arquillian, Cucumber)
# - Message Service (JMS)
# - Web Services (JAX-RS, JAX-WS)
# - Strong understanding of Design and Architectural Patterns
# - Apache Maven
# - Continuous Integration tools (Jenkins or similar)
# - Linux operating system
# - Stash: GIT Repository Management
# - Spoken English language is a must
#
# Nice to have
#
# - Apache Camel
# - Enterprise Integration Patterns
# - Architecture for XML Binding (JAXB)
# - XML Transformations (XSLT, XSD, DTD)
# - FitNesse
# - Drools
# - Agile Methodologies (SCRUM and Kanban)
# - Additional knowledge of financial products is a plus
#
# OCA certificate
#
# Seniority:
#
# Junior"""

JOB_DESCRIPTION_EXAMPLE = """
Looking for a mid software developer.
Skills in:
- Java for 3+ years or other similar programming languages: Scala, Kotlin.
- Open and willing to learn new technologies
- Strong Java Core, Spring Boot knowledge
- Experience with tools like jUnit, Maven and Jenkins
- Good understanding of design patterns
- Developed REST API's using Spring Boot
- Bachelor Degree in Computer Science
"""

if __name__ == "__main__":
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
                pprint(rank_cvs(JOB_DESCRIPTION_EXAMPLE, './cv-directory'))
        else:
            print("The only available option when running the tool are 'train' and 'score'")

