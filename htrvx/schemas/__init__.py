from collections import defaultdict
from typing import Iterable

import os
import click
import requests
from lxml import etree

_here = os.path.dirname(__file__)
Schemas = {
    "ALTO-Segmonto": os.path.join(_here, "", "alto-segmonto.xsd")
}


class Validator:
    def __init__(self, xsd_path: str):
        xmlschema_doc = etree.parse(self.get_schema(xsd_path))
        self.xmlschema = etree.XMLSchema(xmlschema_doc)

    @staticmethod
    def get_schema(xsd_path):
        if xsd_path.startswith("http://") or xsd_path.startswith("https://"):
            schema_req = requests.get(xsd_path)
            schema_req.raise_for_status()
            new_path = "downloaded.xsd"
            with open(new_path, "w") as f:
                f.write(schema_req.text)
            return new_path
        elif xsd_path in Schemas:
            return Schemas[xsd_path]
        return xsd_path


    def validate(self, xml_path: str) -> bool:
        xml_doc = etree.parse(xml_path)
        result = self.xmlschema.validate(xml_doc)

        return result


def simplify_log_line(string: etree._LogEntry) -> str:
    # ToDo: Add cleaning for PAGE as well ?
    return string.message.replace("{http://www.loc.gov/standards/alto/ns-v4#}", "alto:")


def print_error_log(error_log: Iterable[etree._LogEntry], group: bool = False) -> None:
    errors = defaultdict(list)
    for line in error_log:
        if group:
            errors[simplify_log_line(line)].append(str(line.line))
        else:
            click.secho(
                f"\tLine {line.line:04d}: {simplify_log_line(line)}",
                fg="yellow",
                color=True
            )

    for error, lines in errors.items():
        click.secho(
            f"\t{error} on line(s): {', '.join(lines)}",
            fg="yellow",
            color=True
        )


def apply_tests(xsd: str, files: Iterable[str], verbose: bool = False, group: bool = True):
    validator = Validator(xsd)
    failed = False
    errors = []
    for file_name in files:
        if validator.validate(file_name):
            click.echo(f"Testing {file_name}: Valid")
            errors.append(0)
        else:
            failed = True
            click.echo(click.style(f"Testing {file_name}: Invalid", fg="red"), color=True)
            if verbose:
                print_error_log(validator.xmlschema.error_log, group=group)
            errors.append(1)

    click.echo("\n\n\n=====\nREPORT\n=====\n")
    click.echo(f"{sum(errors)}/{len(errors)} invalid XML files")

    return failed
