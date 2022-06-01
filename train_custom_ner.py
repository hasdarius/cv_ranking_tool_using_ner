import os
from pprint import pprint

import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
import csv
import json
import logging
from pathlib import Path
from constants import VALIDATE_TEXT, TEST_TEXT

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
    optimizer.L2_is_weight_decay = True
    optimizer.L2 = 0.01
    optimizer.b1 = 0.9
    optimizer.b2 = 0.999
    optimizer.grad_clip = 1.0
    optimizer.eps = 1e-8
    optimizer.use_radam = False

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    print('Nr iters: ' + str(n_iter) + ' with learning_rate:' + str(learn_rate))
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                for text, annotations in batch:
                    # create Example
                    # texts, annotations = zip(*batch)
                    # nlp.update(
                    #     texts,  # batch of texts
                    #     annotations,  # batch of annotations
                    #     drop=0.2,  # dropout - make it harder to memorise data
                    #     losses=losses,
                    # )
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    # Update the model
                    nlp.update([example], sgd=optimizer, drop=0.2, losses=losses)
            print('Losses', losses)


def save_model(output_dir, new_model_name, nlp):
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


def fine_tune_and_save_custom_model(train_data, model=None, new_model_name=None, output_dir=None):
    learn_rates = [0.001]
    n_iters = [30]
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
            if accuracy >= best_accuracy:
                best_iter = n_iter
                best_learn_rate = learn_rate
                best_accuracy = accuracy
                best_nlp = train_nlp
    save_model(output_dir, new_model_name, nlp=best_nlp)
    print('Iterations: ' + str(best_iter) + ' Learn rate:' + str(best_learn_rate) + ' Accuracy:' + str(best_accuracy))


def get_model_accuracy(input_file, doc2):
    csv_file = open(input_file, 'r')
    csv_file_reader = csv.reader(csv_file)
    all_labeled_data = list(csv_file_reader)
    positive_rows = list(filter(lambda row: row[1] != 'O', all_labeled_data))
    nr_of_entities = len(positive_rows)
    true_positive_matches = 0
    true_negative_matches = len(all_labeled_data) - len(doc2.ents)
    for ent in doc2.ents:
        print([ent.text, ent.label_])
        if [ent.text, ent.label_] in positive_rows:
            true_positive_matches += 1

    precision = true_positive_matches / len(doc2.ents)  # nr_of_entities

    print("True negative matches number: " + str(true_negative_matches))

    print('The precision is:' + str(precision))

    return precision


def validate_model(nlp, input_file):
    doc2 = nlp(VALIDATE_TEXT)
    return get_model_accuracy(input_file, doc2)


def test_model(input_file):
    nlp2 = spacy.load(CUSTOM_SPACY_MODEL)
    validate_model(nlp2, input_file)
