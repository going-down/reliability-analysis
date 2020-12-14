from report import dump_report, LOADS, DEVICE_SCHEME
from utils import read_system_csv, path_join_current
from functools import reduce
import re
import numpy as np

import itertools

import random

import graphviz


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


class Function:
    """
    Part of system.
    If one of functions results as 0 system is not working.

    init: expression string.

    """
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def evaluate(self, loads):
        result = re.findall(r'\(\w+\)', self.expr)
        print(result)

    def print(self):
        print(self.name + ": " + self.expr)


def generate_vectors_single_error(number):
    for i in range(number):
        tmp_vector = np.ones(number, dtype=bool)
        tmp_vector[i] = False
        yield tmp_vector


def generate_vectors_double_error(number):
    for i in range(number - 1):
        for j in range(i + 1, number):
            tmp_vector = np.ones(number, dtype=bool)
            tmp_vector[i] = False
            tmp_vector[j] = False
            yield tmp_vector


def analyze_matrix(matrix):
    length = len(matrix)
    processors = []
    for i in range(2, length):
        row = matrix[i]
        processors.append(Processor(row[0], row[1], row[2], row[3:8]))
    for i in processors:
        i.print()


def analyze_functions(function_string):
    functions = []
    for i in function_string:
        functions.append(Function(i[:2], i[3:]))
    return functions


def evaluate_all(loads, function_string, device_graph):
    analyze_matrix(loads)
    functions = analyze_functions(function_string)
    for i in functions:
        i.evaluate(loads)


def plus(x, y):
    # TODO: implement
    pass


def mult(x, y):
    # TODO: implement
    pass


class ApplierToSSV:
    def apply_to_ssv(self):
        pass


class S(ApplierToSSV):
    def __init__(self, kind, *args):
        self.kind = kind
        self.args = args
        self.op = {
            '+': plus,
            '*': mult
        }

    def apply_to_ssv(self):
        return reduce(self.op[self.kind], self.args)  # I ain't happy with it either


class SchemeElement(ApplierToSSV):
    def __init__(self, i, reject_probability):
        self.i = i
        self.reject_probability = reject_probability


class Pr(SchemeElement):
    def apply_to_ssv(self):
        pass


class A(SchemeElement):
    pass


class B(SchemeElement):
    pass


class C(SchemeElement):
    pass


class D(SchemeElement):
    pass


class M(SchemeElement):
    pass


def pr(i):
    return Pr(i, reject_probability=1.3E-4)


def a(i):
    return A(i, reject_probability=1.2E-4)


def b(i):
    return B(i, reject_probability=2.4E-5)


def c(i):
    return C(i, reject_probability=1.7E-4)


def d(i):
    return C(i, reject_probability=4.2E-4)


def m(i):
    return M(i, reject_probability=3.4E-4)


def Or(*args):
    return S('+', *args)


def And(*args):
    return S('*', *args)


def main(report_path):
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
    loads, function_string = read_system_csv(path_join_current('loads.csv'))
    single_state_error = generate_vectors_single_error(23)
    double_state_error = generate_vectors_double_error(23)

    for i in single_state_error:
        print(i)

    for i in double_state_error:
        print(i)

    # f1=(D1vD2)x(C1vC2)x(B1vB2)x(Pr1vPr2vPr4);;;;;;;;
    # f2=(D2vD3)xC2x(B1vB2)x(Pr3vPr4vA1xM2xA3xB3xPr5);;;;;;;;
    # f3=(D7vD8)xC5xB3x(Pr5vPr6vA2xM1xA1x(B1vB2)xPr2);;;;;;;;
    # f4=D8xC6xB3x(Pr5vPr6v(A2xM1vA3xM2)xA1x(B1vB2)xPr2);;;;;;;;
    f1 = And(Or(d(1), d(2)),
             Or(c(1), c(2)),
             Or(b(1), b(2)),
             Or(pr(1), pr(2), pr(4)))
    f2 = And(Or(d(2), d(3)),
             c(2),
             Or(b(1), b(2)),
             Or(pr(3), pr(4), a(1), m(2), a(3), b(3), pr(5)))
    f3 = And(Or(d(7), d(8)),
             c(5),
             b(3),
             Or(pr(5), pr(6),
                And(a(2), m(1), a(1),
                    Or(b(1), b(2)),
                    pr(2))))
    f4 = And(d(8), c(6), b(3),
             Or(pr(5), pr(6),
                And(Or(And(a(2), m(1)),
                       And(a(3), m(2))),
                    a(1),
                    Or(b(1), b(2)),
                    pr(2))))

    dot = graphviz.Graph()
    for source, targets in device_graph.items():
        for target in targets:
            dot.edge(source, target)
    dot.render(path_join_current('graph.dot'))

    dump_report(
        input={
            LOADS: loads,
            DEVICE_SCHEME: path_join_current('scheme.jpg')
        },
        output=evaluate_all(
            loads=loads,
            function_string=function_string,
            device_graph=device_graph),
        pathname=path_join_current(report_path),
        author=["", ""])


REPORT_PATH = "report.docx"


def place_ones(size, count):
    for positions in itertools.combinations(range(size), count):
        p = [True] * size
        for i in positions:
            p[i] = False
        yield p


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(random.shuffle(list(place_ones(23, 10))))
    main(REPORT_PATH)
    print(len(list(place_ones(23, 3))))

