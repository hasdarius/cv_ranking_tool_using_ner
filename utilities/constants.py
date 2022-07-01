CONCEPTS_SCORES = {
    "intern": {
        "Seniority": 0,
        "Max Programming Language": 2,
        "Max Tool/Framework": 4,
        "Max Certification": 2,
        "Max Programming Concept": 8,
        "Max IT Specialization": 0,
        "Full Programming Language": 7,
        "Partial Programming Language": 3,
        "Full Tool/Framework": 3,
        "Partial Tool/Framework": 1.5,
        "Full Certification": 0,
        "Partial Certification": 0,
        "Full Programming Concept": 5,
        "Partial Programming Concept": 3,
        "Full IT Specialization": 0,
        "Partial IT Specialization": 0
    },
    "junior": {
        "Seniority": 1,
        "Max Programming Language": 4,
        "Max Tool/Framework": 8,
        "Max Certification": 3,
        "Max Programming Concept": 10,
        "Max IT Specialization": 2,
        "Full Programming Language": 7,
        "Partial Programming Language": 3,
        "Full Tool/Framework": 5,
        "Partial Tool/Framework": 2,
        "Full Certification": 1,
        "Partial Certification": 0.5,
        "Full Programming Concept": 3,
        "Partial Programming Concept": 1.5,
        "Full IT Specialization": 1,
        "Partial IT Specialization": 0.5
    },
    "mid": {
        "Seniority": 2,
        "Max Programming Language": 6,
        "Max Tool/Framework": 12,
        "Max Certification": 4,
        "Max Programming Concept": 12,
        "Max IT Specialization": 3,
        "Full Programming Language": 5,
        "Partial Programming Language": 2,
        "Full Tool/Framework": 7,
        "Partial Tool/Framework": 3,
        "Full Certification": 3,
        "Partial Certification": 1.5,
        "Full Programming Concept": 2,
        "Partial Programming Concept": 1,
        "Full IT Specialization": 3,
        "Partial IT Specialization": 1.5
    },
    "senior": {
        "Seniority": 3,
        "Max Programming Language": 8,
        "Max Tool/Framework": 15,
        "Max Certification": 4,
        "Max Programming Concept": 15,
        "Max IT Specialization": 4,
        "Full Programming Language": 5,
        "Partial Programming Language": 2,
        "Full Tool/Framework": 7,
        "Partial Tool/Framework": 3,
        "Full Certification": 4,
        "Partial Certification": 2,
        "Full Programming Concept": 2,
        "Partial Programming Concept": 1,
        "Full IT Specialization": 3,
        "Partial IT Specialization": 1.5
    }
}

LABELS_LIST = ["Programming Language", "Certification", "Seniority", "Tool/Framework", "IT Specialization",
               "Programming Concept"]

REASONING_PERFECT_MATCH = "Full Match: The following word was identified in both the Job description text and in the " \
                          "CV text: "
REASONING_PERFECT_MATCH_TYPE = " being labeled as "
REASONING_PENALIZATION = "You were penalized because we detected too many terms, in relation to your seniority, " \
                         "having the following label: "
REASONING_GRAPH_CONNECTION_P1 = "Partial Match: Although these terms are not alike: "
REASONING_GRAPH_CONNECTION_P2 = " one being found in the Job Description and the other in the CV text, we identified "
REASONING_GRAPH_CONNECTION_P3 = " shortest paths between them, one being the following: "
CV_DIRECTORY = './utils/cv-directory'
TXT_FILES_DIRECTORY = './utils/txt-amr-files'
TTL_FILES_DIRECTORY = './utils/ttl-rdf-files'

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
