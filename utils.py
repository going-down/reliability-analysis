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
        return list(csv.reader(csv_file, delimiter=';'))


def path_join_current(path):
    return os.path.join(pathlib.Path(__file__).parent.absolute(), path)