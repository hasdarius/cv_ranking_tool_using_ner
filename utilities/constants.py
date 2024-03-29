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

CUSTOM_SPACY_MODEL = "Model"

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

JOB_DESCRIPTION_1_PATH = "./utils/job-description-directory/job-description1.txt"
JOB_DESCRIPTION_2_PATH = "./utils/job-description-directory/job-description2.txt"
JOB_DESCRIPTION_3_PATH = "./utils/job-description-directory/job-description3.txt"
JOB_DESCRIPTION_4_PATH = "./utils/job-description-directory/job-description4.txt"

