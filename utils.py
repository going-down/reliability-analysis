import csv
import os
import pathlib


def read_system_csv(path):
    """
    Reads task from .csv
    .csv must contain 8x9 sized load redistribution table
    -----------------------------------------------------
    input:
        path - string with path to file
    output:
        load redistribution table,
        structure functions
    """
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        data = []
        for x in csv_reader:
            data.append(x)
        return data[:7], [x[0] for x in data[9:13]]


def path_join_current(path):
    return os.path.join(pathlib.Path(__file__).parent.absolute(), path)