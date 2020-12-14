from typing import Tuple, Dict, List

from report import dump_report, LOADS, DEVICE_SCHEME
from utils import read_system_csv, path_join_current
from functools import reduce
import re
import numpy as np

import graphviz
from itertools import combinations

import random


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


"""Unnecessary piece of crap till....------"""
#TODO: delete these?

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


"""... till this ------------------------"""


def generate_vectors_multiple_error(blocks_number, error_count, length=0):
    """
    Generates Vi vectors aka System State Vector
    """
    vector = []
    for positions in combinations(range(blocks_number), error_count):
        p = [True] * blocks_number
        for i in positions:
            p[i] = False
        vector.append(p)
    random.shuffle(vector)
    if length == 0:
        return vector
    return vector[:length]


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


class SSVApplierResponse:
    def __init__(self, is_not_failed, rejected_devices):
        self.is_not_failed = is_not_failed
        self.rejected_devices = rejected_devices

    def __repr__(self):
        return {
            'is_not_failed': self.is_not_failed,
            'rejected_devices': self.rejected_devices
        }.__repr__()


def plus(x: SSVApplierResponse, y: SSVApplierResponse) -> SSVApplierResponse:
    """
    OR
    """
    is_not_failed = x.is_not_failed or y.is_not_failed
    rejected_devices = x.rejected_devices + y.rejected_devices
    return SSVApplierResponse(is_not_failed, rejected_devices)


def mult(x: SSVApplierResponse, y: SSVApplierResponse) -> SSVApplierResponse:
    """
    AND
    """
    is_not_failed = x.is_not_failed and y.is_not_failed
    rejected_devices = x.rejected_devices + y.rejected_devices
    return SSVApplierResponse(is_not_failed, rejected_devices)


class ApplierToSSV:
    def apply_to_ssv(self, system_state_vector: Dict[str, List[bool]]) -> SSVApplierResponse:
        pass


class S(ApplierToSSV):
    def __init__(self, kind, *args: ApplierToSSV):
        self.kind = kind
        self.args = args
        self.op = {
            '+': plus,
            '*': mult
        }

    def apply_to_ssv(self, system_state_vector):
        return reduce(self.op[self.kind],
                      [x.apply_to_ssv(system_state_vector) for x in self.args])


class SchemeElement(ApplierToSSV):
    def __init__(self, i, reject_probability, key):
        self.i = i
        self.reject_probability = reject_probability
        self.key = key

    def __repr__(self):
        return {
            self.key: self.i
        }.__repr__()

    def apply_to_ssv(self, system_state_vector):
        is_not_failed = system_state_vector[self.key][self.i]
        return SSVApplierResponse(is_not_failed, [self] if is_not_failed else [])


class Pr(SchemeElement):
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


DEVS = {
    'Pr': dict(),
    'A': dict(),
    'B': dict(),
    'C': dict(),
    'D': dict(),
    'M': dict()
}


def make_dev(init, i, prob, name):
    DEVS[name][i] = init(i, prob, name)
    return DEVS[name][i]


def pr(i):
    return make_dev(Pr, i, 1.3E-4, 'Pr')


def a(i):
    return make_dev(A, i, 1.2E-4, 'A')


def b(i):
    return make_dev(B, i, 2.4E-5, 'B')


def c(i):
    return make_dev(C, i, 1.7E-4, 'C')


def d(i):
    return make_dev(C, i, 4.2E-4, 'D')


def m(i):
    return make_dev(M, i, 3.4E-4, 'M')


def Or(*args):
    return S('+', *args)


def And(*args):
    return S('*', *args)


def bit_vector_to_ssv(bit_vector: List[bool]):
    pr_n = len(DEVS['Pr'].values())
    a_n = pr_n + len(DEVS['A'].values())
    b_n = a_n + len(DEVS['B'].values())
    c_n = b_n + len(DEVS['C'].values())
    d_n = c_n + len(DEVS['D'].values())
    m_n = d_n + len(DEVS['M'].values())
    typed_devs_bits = {
        'Pr': bit_vector[:pr_n],
        'A': bit_vector[pr_n:a_n],
        'B': bit_vector[a_n:b_n],
        'C': bit_vector[b_n:c_n],
        'D': bit_vector[c_n:d_n],
        'M': bit_vector[d_n:m_n]
    }
    return dict(
        (k, dict(
            (dev_i, v[v_i])
            for v_i, dev_i in zip(range(len(v)),
                                  sorted([x for x in DEVS[k].keys()]))))
        for k, v in typed_devs_bits.items())


def ssv_device_probabilities(ssv: Dict[str, Dict[int, bool]],
                             devs: Dict[str, Dict[int, SchemeElement]]):
    for name, devices_states in ssv.items():
        for i, state in devices_states.items():
            dev_rejection_probability = devs[name][i].reject_probability
            yield dev_rejection_probability if state is False else 1. - dev_rejection_probability


def ssv_probability(ssv, devs):
    return reduce((lambda p1, p2: p1 * p2), ssv_device_probabilities(ssv, devs))


def test(f, bit_vectors):
    for bit_vector in bit_vectors:
        ssv = bit_vector_to_ssv(bit_vector)
        resp = f.apply_to_ssv(ssv)
        if not resp.is_not_failed:
            print({
                'prob': ssv_probability(ssv, DEVS),
                'devs': resp.rejected_devices
            })


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

    dev_n = sum(len(typed_devs.values()) for typed_devs in DEVS.values())
    for f in [f1, f2, f3, f4]:
        print("1")
        test(f, generate_vectors_multiple_error(dev_n, 1))
        print("2")
        test(f, generate_vectors_multiple_error(dev_n, 2))
        print("3")
        test(f, generate_vectors_multiple_error(dev_n, 3, 886))
        print("4")
        test(f, generate_vectors_multiple_error(dev_n, 4, 886))
        print()

    dot = graphviz.Graph()
    for source, targets in device_graph.items():
        for target in targets:
            dot.edge(source, target)
    #dot.render(path_join_current('graph.dot'))

    #list_ = list(place_ones(23, 4))
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


#TODO: delete this?
def place_ones(size, count):
    for positions in combinations(range(size), count):
        p = [True] * size
        for i in positions:
            p[i] = False
        yield p


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print(len(list(place_ones(23, 4))))
    #print(random.shuffle(list(place_ones(23, 10))))
    main(REPORT_PATH)
