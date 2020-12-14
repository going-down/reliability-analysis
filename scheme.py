from typing import Dict, List
from functools import reduce


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