#!/usr/bin/env python

import argparse
from itertools import zip_longest

import yaml

from rtofdata.config import data_dir
from rtofdata.create_validation_rules import generate_validation_rules
from rtofdata.excel import read_excel
from rtofdata.word import write_word_specification
from rtofdata.yaml import write_yaml


def mutate_fields(field_list):
    field_list = [{k.lower(): v for k, v in f.items()} for f in field_list]
    field_dict = {f['id']: {**f} for f in field_list}
    for f in field_dict.values():
        del f['id']
        del f['table']

        if "y" in f.get("required", "n").lower():
            f.setdefault('validation', {})['required'] = True

        del f["required"]

        if "date_after" in f:
            f.setdefault('validation', {})['date_after'] = f["date_after"]
            del f["date_after"]

    return field_dict


def get_definition(value):
    v = value[0]
    d = value[1]
    if d is None:
        return v
    else:
        return dict(value=v, description=d)


def main(filename):
    data = read_excel(filename, as_list=["Categories"])

    record_list = [dict(id=r['Table'], description=r['Description'].strip()) for r in data['Tables']]
    for record in record_list:
        record['fields'] = mutate_fields([f for f in data['Fields'] if f['Table'] == record['id']])

        with open(data_dir / 'records' / f'{record["id"]}.yml', 'wt') as file:
            file_contents = dict(description=record['description'], fields=record['fields'])
            yaml.dump(file_contents, file, sort_keys=False)

    category_list = data['Categories']
    category_ids = [id for id in category_list.keys() if not id.endswith("_description")]

    for key in category_ids:
        values = category_list[key]
        descriptions = category_list.get(f"{key}_description", [])
        values = zip_longest(values, descriptions)
        values = [get_definition(v) for v in values]

        with open(data_dir / 'categories' / f'{key}.yml', 'wt') as file:
            yaml.dump(values, file, sort_keys=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process the RTOF data specification'
    )
    parser.add_argument('filename', type=str, help='The filename to read')

    args = parser.parse_args()

    main(args.filename)