from os import path
from pprint import pprint

import train_custom_ner
from cv_scorer import rank_cvs


def main(input_file):
    if not path.exists(train_custom_ner.CUSTOM_SPACY_MODEL):
        json_file_name = train_custom_ner.csv_to_json_with_labels(input_file, '-')
        training_data = train_custom_ner.json_to_spacy_format(json_file_name)
        train_custom_ner.fine_tune_and_save_custom_model(training_data,
                                                         new_model_name='technology_it_model',
                                                         output_dir=train_custom_ner.CUSTOM_SPACY_MODEL)
    pprint(rank_cvs(JOB_DESCRIPTION_EXAMPLE, 'D:/faculta/licenta/cv-directory'))


JOB_DESCRIPTION_EXAMPLE = """Skills

Must have

- Mandatory Computer Science Faculty / Cybernetics / Mathematics / Informatics graduated
- Min 1 Year working hands on experience in Java Python Scala Ruby
- Java 8
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
