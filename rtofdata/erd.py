from pathlib import Path

import graphviz
from jinja2 import Environment, FileSystemLoader, select_autoescape

from rtofdata.config import output_dir, assets_dir
from rtofdata.spec_parser import Specification


def create_erd(spec: Specification):
    env = Environment(
        loader=FileSystemLoader(assets_dir),
        autoescape=select_autoescape()
    )
    spec.records_by_flow
    relationships = []
    for r in spec.records:
        pk = r.primary_keys
        for f in r.fields:
            if f.foreign_keys:
                for fk in f.foreign_keys:
                    lh_c = "0,1" if pk == [f] else "0..N"
                    relationships.append(dict(lh=r.id, rh=fk['record'], lh_c=lh_c, rh_c=1))

    context = dict(spec=spec, relationships=relationships)

    template = env.get_template("dot-template.txt")
    output_filename = output_dir / "record-relationships.dot"
    with open(output_filename, "wt") as file:
        file.write(template.render(context))

    path = graphviz.render("circo", "png", output_filename)
    Path(path).rename(output_dir / "record-relationships.png")