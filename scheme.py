from typing import Dict, List
from functools import reduce
from abc import ABC, abstractmethod

from report import DumpAble


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


class TreeNode:
    def flatten(self) -> List:
        return [self]


class ApplierToSSV(DumpAble, TreeNode):
    @abstractmethod
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

    op_dump_map = {
        '+': lambda x, y: "%s ∨ %s" % (x, y),
        '*': lambda x, y: "%s ∧ %s" % (x, y)
    }

    def flatten(self):
        return reduce(lambda list1, list2: list1 + list2, [x.flatten() for x in self.args])

    def dump(self):
        return reduce(self.op_dump_map[self.kind],
                      ('('+x.dump()+')' if isinstance(x, S) and x.kind == '+' else x.dump()
                       for x in self.args))

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

    def dump(self):
        return "%s%s" % (self.key, self.i)

    def apply_to_ssv(self, system_state_vector):
        is_not_failed = system_state_vector[self.key][self.i]
        return SSVApplierResponse(is_not_failed, [] if is_not_failed else [self])


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
