import csv
import pathlib
from report import dump_report


def evaluate_all(reject_probabilities, device_graph):
    pass


def read_matrix(path):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        return [x for x in csv_reader]


def main():
    path = "loads.csv"
    dir_path = pathlib.Path(__file__).parent.absolute()
    loads = read_matrix(dir_path.__str__() + "\\" + path)
    for i in loads:
        print(i)
        print("\n")

    reject_probabilities = {
        'Pr': 1.3E-4,
        'A': 1.2E-4,
        'B': 2.4E-5,
        'C': 1.7E-4,
        'D': 4.2E-5,
        'M': 3.4E-4
    }
    device_graph = {
        'B1': {'Pr1', 'Pr2', 'Pr3', 'Pr4', 'A1', 'C1', 'C2'},
        'B2': {'Pr1', 'Pr2', 'Pr3', 'Pr4', 'A1', 'C1', 'C2'},
        'C1': {'D1', 'D2'},
        'C2': {'D2', 'D3'},
        'M1': {'A1', 'A2'},
        'M2': {'A1', 'A3'},
        'B3': {'A2', 'A3', 'Pr5', 'Pr6', 'C5', 'C6'},
        'C5': {'D7', 'D8'},
        'C6': {'D8'}
    }
    dump_report(evaluate_all(reject_probabilities, device_graph),
                "report.docx",
                ["", ""])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
