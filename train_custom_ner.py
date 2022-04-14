import os

import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
import csv
import json
import logging
from pathlib import Path

LABEL = ['Programming Language', 'Certification', 'Seniority', 'Tool/Framework', 'IT Specialization',
         'Programming Concept']
CUSTOM_SPACY_MODEL = 'Model'


def create_tsv_file(input_path):
    csv_file = open(input_path, 'r')
    csv_file_reader = csv.reader(csv_file)
    input_file_name, _ = os.path.splitext(input_path)
    tsv_file_name = input_file_name + '.tsv'
    tsv_file = open(tsv_file_name, 'wt', newline='')
    tsv_file_writer = csv.writer(tsv_file, delimiter='\t')
    rows = ((r[0], r[1]) for r in csv_file_reader)
    tsv_file_writer.writerows(rows)
    csv_file.close()
    tsv_file.close()
    return tsv_file_name


def csv_to_json_with_labels(input_path, unknown_label):
    tsv_file_name = create_tsv_file(input_path)
    try:
        tsv_file = open(tsv_file_name, 'r')  # input file
        input_file_name, _ = os.path.splitext(input_path)
        output_file_name = input_file_name + '.json'
        output_file = open(output_file_name, 'w')  # output file
        data_dict = {}
        annotations = []
        label_dict = {}
        s = ''
        start = 0
        for line in tsv_file:
            if line[0:len(line) - 1] != '.\tO':
                word, entity = line.split('\t')
                s += word + " "
                entity = entity[:len(entity) - 1]
                if entity != unknown_label and len(entity) != 1:
                    d = {'text': word, 'start': start, 'end': start + len(word) - 1}
                    try:
                        label_dict[entity].append(d)
                    except:
                        label_dict[entity] = []
                        label_dict[entity].append(d)
                start += len(word) + 1
            else:
                data_dict['content'] = s
                s = ''
                label_list = []
                for entities in list(label_dict.keys()):
                    for i in range(len(label_dict[entities])):
                        if label_dict[entities][i]['text'] != '':
                            l = [entities, label_dict[entities][i]]
                            for j in range(i + 1, len(label_dict[entities])):
                                if label_dict[entities][i]['text'] == label_dict[entities][j]['text']:
                                    di = {'start': label_dict[entities][j]['start'],
                                          'end': label_dict[entities][j]['end'],
                                          'text': label_dict[entities][i]['text']}
                                    l.append(di)
                                    label_dict[entities][j]['text'] = ''
                            label_list.append(l)

                for entities in label_list:
                    label = {'label': [entities[0]], 'points': entities[1:]}
                    annotations.append(label)
                data_dict['annotation'] = annotations
                annotations = []
                json.dump(data_dict, output_file)
                output_file.write('\n')
                data_dict = {}
                start = 0
                label_dict = {}
        tsv_file.close()
        os.remove(tsv_file_name)
        return output_file_name
    except Exception as e:
        logging.exception("Unable to process file" + "\n" + "error = " + str(e))
        return None


def json_to_spacy_format(input_file):
    try:
        training_data = []
        lines = []
        output_file, _ = os.path.splitext(input_file)
        with open(input_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            entities = []
            for annotation in data['annotation']:
                point = annotation['points'][0]
                labels = annotation['label']
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    entities.append((point['start'], point['end'] + 1, label))

            training_data.append((text, {"entities": entities}))

        os.remove(input_file)
        return training_data
    except Exception as e:
        logging.exception("Unable to process " + input_file + "\n" + "error = " + str(e))
        return None


def train_model(n_iter, train_data, model, learn_rate, nlp):
    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.create_optimizer()

    optimizer.learn_rate = learn_rate
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    print(n_iter)
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                for text, annotations in batch:
                    # create Example
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    # Update the model
                    nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
            # print('Losses', losses)


def save_model(output_dir, new_model_name, nlp):
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


def validate_model(nlp, input_file):
    # Test the saved model
    validate_text = """Wanted: Java Engineer with experience in building high-performing, scalable, enterprise-grade applications.
You need to have proven knowledge in Web applications with JEE/Spring, DevOps experience with high focus on cloud-based operating systems (particularly AWS), Jenkins, Docker and Kubernetes are a plus.
Looking for people with experience in Kafka, Big-Data and Python.
Must have experience with build tools (Maven, Gradle) and a Object-Oriented Analysis and design using common design patterns.
Hiring people with good knowledge of Relational Databases, PostgreSQL and ORM technologies (JPA, Hibernate).
Orientation towards test-driven development and clean code is a plus
Requirements: experience with version control systems (Git) and a Bachelor/Master degree in Computer Science, Engineering, or a related subject.
You need to have development experience in Java and Java frameworks and SQL/Relational Databases skills.
One requirement is having practical skills in CI/CD - some of Git, Maven, Gradle, Docker, Jenkins, Jira.
Skills description: 4+ years’ experience with Java (developing backend/web applications, Java 8+), 3+ years’ experience with Spring Boot (Spring Data, Spring Cloud), good unit/integration testing experience.
Nice-to-Have Skills: experience with software provisioning/configuration (e.g. Puppet, Ansible), with Oracle  and Angular 2+.
We are looking for: experience in Apache Camel, experience with MSSQL, PostgreSQL, experience with Unit and integration testing with JUnit and Mockito, CI/CD tools: Git, Jenkins, Maven, SonarQube, Artifactory and Microservices, Dockers, and Kubernetes.
Nice to have: exposure to NoSQL databases (MongoDBB), exposure to Python, Jupyter Hub.
Requirements: strong knowledge of Java Fundamentals and OOP principles and good understanding of design patterns.
At the moment we're using a mix of Python and Javascript.
We know you want to know so here is the stack: Python, Django, React, Redux, Express.
Other buzzwords: Universal Web Apps, Machine Learning, Heroku, AWS, Algolia.
Have already used at least one of these technologies amongst JavaScript, TypeScript, React, Vue.js, Kafka, ElasticSearch, MongoDB, and Python.
The general tech stack of the project is: iOS (Swift), Android (Kotlin), Modern Web Apps (Angular, React), Microservice architecture with OpenAPI contracts.
Basic qualifications: experience with web application development (.NET/JavaScript or equivalent).
Open to work with other programming languages (Python, Scala).
Qualifications and Experience: Knowledge of Spring (Boot, Data, Security).
University degree in a technical subject (Computer Science, Mathematics, or similar) or equivalent experience in the industry.
Qualifications: FPGA Digital Design experience, C++, Qt framework experience
The requirements are the following: knowledge of .Net, .Net Core, WebAPI, ASP.Net MVC, Razor Views or equivalent single page application framework, C#, JavaScript, CSS, HTML5 & Azure Cloud services or AWS, Active Directory.
You need to have experience with the ASP.NET framework and ideally SQL Server.
Capability to design complex SQL queries.
You know the ins and outs of several cloud providers like AWS, Azure, Heroku and profound experience in Terraform, Google Cloud.
Here are the technologies you must have experience with: Django, Node.js, Nginx, React, React Native, Redis, RabbitMQ.
The following are a must: Selenium, Grafana."""
    # print("Loading from custom model named:", model)
    # nlp2 = spacy.load(model)
    doc2 = nlp(validate_text)
    csv_file = open(input_file, 'r')
    csv_file_reader = csv.reader(csv_file)
    rows = list(filter(lambda row: row[1] != 'O', list(csv_file_reader)))
    print(rows)
    nr_of_entities = len(rows)
    nr_of_matches = 0
    for ent in doc2.ents:
        if [ent.text, ent.label_] in rows:
            print(ent.label_, ent.text)
            nr_of_matches += 1
    accuracy = nr_of_matches / nr_of_entities
    print(accuracy)
    return accuracy


def fine_tune_and_save_custom_model(train_data, model=None, new_model_name=None, output_dir=None):
    learn_rates = [0.1, 0.05, 0.01, 0.005, 0.001]
    n_iters = [10, 20, 50, 100, 150, 200, 250, 300]
    """Setting up the pipeline and entity recognizer, and training the new entity."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spacy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")
    if 'ner' not in nlp.pipe_names:
        nlp.create_pipe('ner')
        nlp.add_pipe('ner')
    ner = nlp.get_pipe('ner')

    for i in LABEL:
        ner.add_label(i)  # Add new entity labels to entity recognizer

    best_nlp = nlp
    best_accuracy = 0
    best_learn_rate = learn_rates[0]
    best_iter = n_iters[0]

    for n_iter in n_iters:
        for learn_rate in learn_rates:
            train_nlp = nlp
            train_model(n_iter, train_data, model=model, learn_rate=learn_rate, nlp=train_nlp)
            accuracy = validate_model(train_nlp, 'Data/validate.csv')
            if accuracy > best_accuracy:
                best_iter = n_iter
                best_learn_rate = learn_rate
                best_accuracy = accuracy
                best_nlp = train_nlp
    save_model(output_dir, new_model_name, nlp=best_nlp)
    print('Iterations: ' + str(best_iter) + ' Learn rate:' + str(best_learn_rate) + ' Accuracy:' + str(best_accuracy))