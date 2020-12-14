from scheme import *

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