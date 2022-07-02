import csv
import logging
import os
import random
import shutil
from pathlib import Path
from pprint import pprint
from sys import path

import spacy
from spacy.scorer import Scorer
from spacy.training.example import Example
from spacy.util import minibatch, compounding

from utilities.constants import LABELS_LIST

CUSTOM_SPACY_MODEL = 'Model'


def csv_to_spacy_format(input_path, unknown_label='-'):
    try:
        csv_file = open(input_path, 'r')
        csv_file_reader = csv.reader(csv_file)
        rows = ((r[0], r[1]) for r in csv_file_reader)
        input_file_name, _ = os.path.splitext(input_path)
        training_data = []
        entities_list = []
        sentence = ''
        start = 0
        for row in rows:
            if row[0] + ',' + row[1] != '.,O':
                word, entity = row[0], row[1]
                sentence += word + " "
                entity = entity[:len(entity)]
                if entity != unknown_label and len(entity) != 1:
                    new_occurrence = (start, start + len(word), entity)
                    entities_list.append(new_occurrence)
                start += len(word) + 1
            else:
                training_data.append((sentence, {"entities": entities_list}))
                start = 0
                sentence = ''
                entities_list = []
        csv_file.close()
        return training_data
    except Exception as e:
        logging.exception("Unable to process file" + "\n" + "error = " + str(e))
        return None


def train_model(n_iter, train_data, model, learn_rate, nlp):
    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.create_optimizer()
    optimizer.learn_rate = learn_rate
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    print('Nr iters: ' + str(n_iter) + ' with learning_rate:' + str(learn_rate))
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                for text, annotations in batch:
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
    learn_rates = [0.001, 0.005]
    n_iters = [20, 30, 40, 50, 60, 70]
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

    for i in LABELS_LIST:
        ner.add_label(i)  # Add new entity labels to entity recognizer

    best_nlp = nlp
    best_f1_score = 0
    best_learn_rate = learn_rates[0]
    best_iter = n_iters[0]

    for n_iter in n_iters:
        for learn_rate in learn_rates:
            train_nlp = nlp
            train_model(n_iter, train_data, model=model, learn_rate=learn_rate, nlp=train_nlp)
            f1_score = evaluate_model(train_nlp, 'Data/validate.csv')
            if f1_score >= best_f1_score:
                best_iter = n_iter
                best_learn_rate = learn_rate
                best_f1_score = f1_score
                best_nlp = train_nlp
    best_f1_score = evaluate_model(best_nlp, 'Data/test.csv')
    print('After hyperparameter tuning -> model: ' + 'Iterations: ' + str(best_iter) + ' Learn rate:' + str(
        best_learn_rate) + ' F1 Score:' + str(best_f1_score))
    save_model(output_dir, new_model_name, nlp=best_nlp)


def evaluate_model(nlp, input_file):
    validate_data = csv_to_spacy_format(input_file)
    examples = []
    scorer = Scorer()
    for text, annotations in validate_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        example.predicted = nlp(str(example.predicted))
        examples.append(example)
    scores = scorer.score(examples)
    print('Evaluation of model:')
    pprint(scores)
    print('---------------------')
    f1_score = scores['ents_f']
    return f1_score


def begin_training():
    if path.exists(CUSTOM_SPACY_MODEL):
        shutil.rmtree(CUSTOM_SPACY_MODEL)
    training_data = csv_to_spacy_format('Data/train.csv', '-')
    fine_tune_and_save_custom_model(training_data,
                                    new_model_name='technology_it_model',
                                    output_dir=CUSTOM_SPACY_MODEL)
