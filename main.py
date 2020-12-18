from typing import Dict, List
from functools import reduce
from collections import OrderedDict

import graphviz
import random
import itertools
import more_itertools

from utils import read_system_csv, path_join_current
from report import dump_report, LOADS, DEVICE_SCHEME, FNS, DumpAble
from system import pr, a, b, c, d, m, DEVS, And, Or, SchemeElement, SSVApplierResponse, Pr, ApplierToSSV, S


class ProcessorLoadBalancer:
    def __init__(self, i, name, t_n, t_max, replace_processors):
        self.i = i
        self.name = name
        self.t_n = t_n
        self.t_max = t_max
        self.replace_processors = replace_processors


class FailedDevsStatistics:
    def __init__(self, devices: Dict[str, Dict[int, SchemeElement]]):
        self.devs = {}
        tmp = {}
        diction = devices
        for dev_category in diction:
            for dev_id in diction[dev_category]:
                dev = diction[dev_category][dev_id]
                tmp[dev.key + dev.i.__str__()] = 0
            od = OrderedDict(sorted(tmp.items()))
            self.devs.update(od)
            tmp = {}

    def recalc(self, failed_devs: Dict[str, Dict[bool, List[bool]]]):
        for dev_category in failed_devs:
            for dev in failed_devs[dev_category]:
                if not failed_devs[dev_category][dev]:
                    self.devs[dev_category + dev.__str__()] += 1

    def zero(self):
        for dev in self.devs:
            self.devs[dev] = 0

    def print(self):
        for dev in self.devs:
            print(dev + ";" + self.devs[dev].__str__() + ";")


def generate_vectors_multiple_error(blocks_number, error_count, length=0):
    """
    Generates Vi vectors aka System State Vector
    """
    vector = []
    for positions in itertools.combinations(range(blocks_number), error_count):
        p = [True] * blocks_number
        for i in positions:
            p[i] = False
        vector.append(p)
    random.shuffle(vector)
    if length < 1:
        return vector
    return vector[:length]


def matrix_to_processor_load_balancers(matrix: List[List]) -> Dict[int, ProcessorLoadBalancer]:
    return dict([(i, ProcessorLoadBalancer(i,
                                           row[0],
                                           int(row[1]),
                                           int(row[2]),
                                           dict((i, int(col)) for i, col in enumerate(row[3:], start=1))))
                 for i, row in enumerate(matrix[2:], start=1)])


class LoadBalanceAble:
    def balance_load(self,
                     ssv,
                     trivial_response: SSVApplierResponse,
                     balance_scheme: Dict[int, ProcessorLoadBalancer]) -> SSVApplierResponse:
        pass


def enumerate_devs(devs):
    return dict((dev.i, dev) for dev in devs)


class TaskFunction(LoadBalanceAble, ApplierToSSV, DumpAble):
    def __init__(self, expr: S):
        self.expr = expr

    def apply_to_ssv(self, system_state_vector: Dict[str, List[bool]]) -> SSVApplierResponse:
        return self.expr.apply_to_ssv(system_state_vector)

    def dump(self):
        return self.expr.dump()

    def balance_load(self,
                     ssv,
                     trivial_response: SSVApplierResponse,
                     balancing_scheme: Dict[int, ProcessorLoadBalancer]) -> SSVApplierResponse:
        if trivial_response.is_not_failed is True or \
                not all(isinstance(dev, Pr) for dev in trivial_response.rejected_devices):
            return trivial_response
        else:
            rejected_processors = list(filter(lambda i: not ssv['Pr'][i], ssv['Pr']))
            available_i_s = list(filter(lambda i: i not in rejected_processors, balancing_scheme))

            balancing_scheme_for_failed = dict((i, dict((j, balancing_scheme[i].replace_processors[j])
                                                        for j in available_i_s))
                                               for i in rejected_processors)

            all_possible_replacements = dict((i, list(more_itertools.powerset([x for x in row.keys()])))
                                             for i, row in balancing_scheme_for_failed.items())

            def filter_if_covers(i, combs):
                return list(
                    filter(lambda combination: balancing_scheme[i].t_n <= sum(balancing_scheme[i].replace_processors[r]
                                                                              for r in combination),
                           combs))

            filtered_replacements = dict((i, filter_if_covers(i, combinations))
                                         for i, combinations in all_possible_replacements.items())
            filtered_replacements_keys = filtered_replacements.keys()
            filtered_replacements_values = [filtered_replacements[i] for i in filtered_replacements_keys]

            def is_fitting_configuration(conf):
                t_s = dict()
                for replacement_i_s, old_i in zip(conf, filtered_replacements_keys):
                    for replacement_i in replacement_i_s:
                        t_s[replacement_i] = t_s.get(replacement_i, 0) + \
                                             balancing_scheme[old_i].replace_processors[replacement_i]
                return all(t_s[i] <= balancing_scheme[i].t_max for i in t_s.keys())

            try:
                fitting_configuration = next(x for x in itertools.product(*filtered_replacements_values)
                                             if is_fitting_configuration(x))
                #print("YIS")
                return SSVApplierResponse(True, [])
            except StopIteration:
                #print("Could not balance the load " + rejected_processors.__str__() + "  " + available_i_s.__str__())
                return trivial_response


def analyze_function(f, bit_vectors, failed_devs: FailedDevsStatistics, balancing_scheme):
    summary = 0.0
    fails = 0
    fixes = 0
    passes = 0
    for bit_vector in bit_vectors:
        ssv = bit_vector_to_ssv(bit_vector)
        resp = f.apply_to_ssv(ssv)
        resp_with_balancing = f.balance_load(ssv, resp, balancing_scheme)
        failed_devs.recalc(ssv)
        if not resp.is_not_failed:
            summary = summary + ssv_probability(ssv, DEVS)
            fails += 1
            if resp_with_balancing.is_not_failed:
                fixes += 1
        else:
            passes += 1
    #print(summary)
    #print("failed " + fails.__str__())
    return summary, passes, fails, fixes, len(bit_vectors)


def evaluate_all(loads, fns, device_graph):
    dev_n = sum(len(typed_devs.values()) for typed_devs in DEVS.values())
    tmp_var = DEVS.values()
    iteret = 0
    fd_statistics = FailedDevsStatistics(DEVS)
    fd_statistics.zero()
    """for f in fns:
        summary = 0
        print("f" + iteret.__str__())
        print("1-x error")
        summary += analyze_function(f, generate_vectors_multiple_error(dev_n, 1), failed_devs)
        print("2-x error")
        summary += analyze_function(f, generate_vectors_multiple_error(dev_n, 2), failed_devs)
        print("3-x error")
        summary += 2 * analyze_function(f, generate_vectors_multiple_error(dev_n, 3, 886), failed_devs)
        print("4-x error")
        summary += 10 * analyze_function(f, generate_vectors_multiple_error(dev_n, 4, 886), failed_devs)
        print(summary)
        print()
        iteret = iteret + 1"""

    balancing_scheme = matrix_to_processor_load_balancers(loads)
    print("vectors_count;rejection_count;fi;passes;fails;fixes;unrecoverable;q for fi")
    summary_summary = 0
    for rejection_count, count, mult in [[1, 0, 1], [2, 0, 1], [3, 886, 2], [4, 886, 10]]:
        summary = 0
        SSVs = generate_vectors_multiple_error(dev_n, rejection_count, count)
        for i, f in enumerate(fns):
            p, passes, fails, fixes, vectors_count = analyze_function(f, SSVs, fd_statistics, balancing_scheme)
            print("%i;error %i;f%i;%i;%i;%i;%i;%e" % (vectors_count, rejection_count, i, passes, fails, fixes, (fails - fixes), p))
            summary += p
        summary_summary += summary*mult
    print()
    print("Summary Q=", summary_summary)
    print()
    # print(summary)
    # print()

    fd_statistics.print()
    fd_statistics.zero()


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
    loads = read_system_csv(path_join_current('loads.csv'))
    # f1=(D1vD2)x(C1vC2)x(B1vB2)x(Pr1vPr2vPr4);;;;;;;;
    # f2=(D2vD3)xC2x(B1vB2)x(Pr3vPr4vA1xM2xA3xB3xPr5);;;;;;;;
    # f3=(D7vD8)xC5xB3x(Pr5vPr6vA2xM1xA1x(B1vB2)xPr2);;;;;;;;
    # f4=D8xC6xB3x(Pr5vPr6v(A2xM1vA3xM2)xA1x(B1vB2)xPr2);;;;;;;;
    f1 = TaskFunction(
        And(Or(d(1), d(2)),
            Or(c(1), c(2)),
            Or(b(1), b(2)),
            pr(1)))
    f2 = TaskFunction(
        And(Or(d(2), d(3)),
            c(2),
            Or(b(1), b(2)),
            Or(pr(3), pr(4), a(1), m(2), a(3), b(3), pr(5))))
    f3 = TaskFunction(
        And(Or(d(7), d(8)),
            c(5),
            b(3),
            Or(pr(5), pr(6),
               And(a(2), m(1), a(1),
                   Or(b(1), b(2)),
                   pr(2)))))
    f4 = TaskFunction(
        And(d(8), c(6), b(3),
            Or(pr(5), pr(6),
               And(Or(And(a(2), m(1)),
                      And(a(3), m(2))),
                   a(1),
                   Or(b(1), b(2)),
                   pr(2)))))
    dot = graphviz.Graph()
    for source, targets in device_graph.items():
        for target in targets:
            dot.edge(source, target)
    # dot.render(path_join_current('graph.dot'))

    dump_report(
        data={
            FNS: [f1, f2, f3, f4],
            LOADS: loads,
            DEVICE_SCHEME: path_join_current('scheme.jpg')
        },
        output=evaluate_all(
            loads=loads,
            fns=[f1, f2, f3, f4],
            device_graph=device_graph),
        pathname=path_join_current(report_path),
        author=["", ""])


REPORT_PATH = "report.docx"
if __name__ == '__main__':
    main(REPORT_PATH)
