from report import dump_report, LOADS, DEVICE_SCHEME
from utils import read_system_csv, path_join_current


class Module:
    """
    Module of system, such as
    Prn(processor number n),
    Bn(bus number n),
    Mn(magistral?? number n),
    An(Adapter number n),
    Cn(connector?? n),
    Dn(sensor?? n)
    """
    def __init__(self, name):
        self.name = name


class Processor:
    def __init__(self, name, t_n, t_max, replace_processors):
        self.name = name
        self.t_n = t_n
        self.t_max = t_max
        self.replace_processors = replace_processors

    def print(self):
        print(self.name + ": " + self.t_n + " " + self.t_max + " ", self.replace_processors)


def analyze_matrix(matrix):
    length = len(matrix)
    processors = []
    for i in range(2, length):
        row = matrix[i]
        processors.append(Processor(row[0], row[1], row[2], row[3:]))
    for i in processors:
        i.print()


def evaluate_all(loads, reject_probabilities, device_graph):
    analyze_matrix(loads)


def main(report_path):
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
    loads, functions = read_system_csv(path_join_current('loads.csv'))
    dump_report(
        input={
            LOADS: loads,
            DEVICE_SCHEME: path_join_current('scheme.jpg')
        },
        output=evaluate_all(
            loads=loads,
            reject_probabilities=reject_probabilities,
            device_graph=device_graph),
        pathname=path_join_current(report_path),
        author=["", ""])


REPORT_PATH = "report.docx"


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(REPORT_PATH)
