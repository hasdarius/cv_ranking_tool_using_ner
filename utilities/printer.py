from pprint import pprint


def print_entities_from_text(sentence_type, text, entities):
    print("-----------------------------")
    print("For the " + sentence_type +":\n" + text + "\nThe entities extracted by the NER model are:\n")
    pprint(entities)
    print("-----------------------------")