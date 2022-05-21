import amrlib

from datetime import datetime


def initialize_nodes_neighbours(input_text):
    stog = amrlib.load_stog_model()
    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f")
    print("date and time =", dt_string)
    graphs = stog.parse_sents([input_text])  # 'I love Computer Science and my main passion is Python.'
    filename = "cv-amr-" + dt_string + ".txt"
    f = open(filename, "w+")
    f.write("# ::id " + filename + " ::date " + dt_string + "\n")
    for graph in graphs:
        print(graph)
        f.write(graph)
    f.close()


if __name__ == "__main__":
    initialize_nodes_neighbours('I love Computer Science and my main passion is Python.')
