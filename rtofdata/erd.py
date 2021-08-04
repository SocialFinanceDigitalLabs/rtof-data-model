from eralchemy import render_er
import pygraphviz as pgv

from rtofdata.config import output_dir
from rtofdata.spec_parser import Specification


def create_erd(spec: Specification):
    output_file = str(output_dir / "record-relationships.er")
    with open(output_file, "wt") as file:
        print("# Entities\n", file=file)

        for r in spec.records_by_flow:
            r = r.record
            print(f"[{r.id}]", file=file)
            for f in r.fields:
                field_desc = f'{f.id} {{label:"{f.type}"}}'
                if f.primary_key:
                    field_desc = f"*{field_desc}"
                print(f"  {field_desc}", file=file)
            print("", file=file)

        print("\n# Relationships\n", file=file)
        for r in spec.records:
            for f in r.fields:
                if f.foreign_keys:
                    for fk in f.foreign_keys:
                        print(f"{r.id:25} *--1   {fk['record']} {{label:\"{fk['field']}\"}}", file=file)

    render_er(output_file, str(output_dir / "record-relationships.dot"))
    render_er(output_file, str(output_dir / "record-relationships.png"))

    G = pgv.AGraph(str(output_dir / "record-relationships.dot"))
    G.draw(str(output_dir / "record-relationships2.png"), prog="circo")

