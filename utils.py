import csv
import os
import pathlib


def read_matrix(path):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        return [x for x in csv_reader]


def path_join_current(path):
    return os.path.join(pathlib.Path(__file__).parent.absolute(), path)