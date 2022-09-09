from collections import defaultdict
from typing import Iterable, List, Literal, Dict, Optional, Tuple

import click
from lxml import etree

from htrvx.schemas import Validator, simplify_log_line
from htrvx.zones import AltoXML, PageXML, Element
from dataclasses import dataclass

Space1 = "  "
Space2 = "    "


def _color(status):
    if status == "success":
        return "green"
    elif status == "warning":
        return "yellow"
    else:
        return "red"


def _char(status):
    if status == "success":
        return "✓"
    elif status == "warning":
        return "⚠"
    else:
        return "×"


def _msg(status):
    if status == "success":
        return "passed successfully"
    elif status == "warning":
        return "has warnings"
    else:
        return "failed"


@dataclass
class Status:
    status: Literal["success", "warning", "failure"]
    task: Literal["segmonto", "schema", "empty-verification"]
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    level: Optional[Literal["zone", "line"]] = None

    def print(self):
        additional_info = ""
        if self.level:
            additional_info = f" at the \033[1m{self.level}\033[0m's level"

        click.echo(
            click.style(
                f"{Space1}{_char(self.status)} \033[1m{' '.join(self.task.capitalize().split('-'))}\033[0m's "
                f"test{additional_info} {_msg(status=self.status)}{': '+self.message if self.message else ''}.",
                fg=_color(self.status)
            )
        )
        if self.errors:
            for error in self.errors:
                click.echo(click.style(f"{Space2}┗ {error}", fg="blue"))


@dataclass
class FileLog:
    tests: Optional[List[Status]] = None

    def append(self, value):
        if self.tests is None:
            self.tests = []
        self.tests.append(value)

    @property
    def status(self):
        passed, total = self.score
        return passed == total

    @property
    def score(self) -> Tuple[int, int]:
        """Returns the number of passing test and test done"""
        statuses = [
            0 if file_status.status == "failure" else 1
            for file_status in self.tests
        ]
        return sum(statuses), len(self.tests)

    def __iter__(self):
        return iter(self.tests)

    def __len__(self):
        return self.tests

    def __bool__(self):
        return self.status

    def print(self):
        if self.tests:
            for element in self.tests:
                element.print()


def _empty_or_wrong(category):
    if category is None:
        return "is not categorized"
    return f"has a forbidden type (`{category}`)"


def _get_ids(ids):
    return ", ".join([f"#{val}" for val in ids])


def parse_segmonto_errors(errors: Iterable[Element], group=False, element_type="element") -> List[str]:
    """ Parse a list of errors
    
    """
    if not errors:
        return []

    if not group:
        return [
            f"{element_type.capitalize()} with id #{error.id} {_empty_or_wrong(error.category)}"
            for error in errors
        ]

    groups = defaultdict(list)
    for error in errors:
        groups[f"`{error.category}`" if error.category is not None else "Missing"].append(error.id)

    return [
        f"{tag_name} tag for {element_type}(s) is forbidden ({len(ids)} annotations): {_get_ids(ids)}"
        for tag_name, ids in sorted(list(groups.items()), key=lambda x: x[0])
    ]


def parse_empty(empty, group=False) -> Tuple[List[str], List[str]]:
    """ Parses the empty log and returns two list of errors: one for lines, one for regions

    """
    if not empty:
        return [], []

    zone_errors = [z.id for z in empty if z.tagname == "Region"]
    line_errors = [z.id for z in empty if z.tagname == "Line"]

    if not group:
        return (
            [f"Region with id #{zone} is empty" for zone in zone_errors],
            [f"Line with id #{line} is empty" for line in line_errors]
        )
    return (
        [f"{_get_ids(zone_errors)}"],
        [f"{_get_ids(line_errors)}"]
    )


def parse_alto_logs(error_log: Iterable[etree._LogEntry], group: bool = False) -> List[str]:
    """ Parses a Schema error log and returns the error with simplifications as string

    """
    if not group:
        return [
            f"Line {line.line:04d}: {simplify_log_line(line)}"
            for line in error_log
        ]
    errors = defaultdict(list)
    for line in error_log:
        if group:
            errors[simplify_log_line(line)].append(str(line.line))

    return [
        f"{error} on line(s): {', '.join(lines)}"
        for error, lines in errors.items()
    ]


def test(
        files: Iterable[str],
        verbose: bool = False,
        group: bool = True,
        format: str = "alto",
        segmonto: bool = True,
        check_empty: bool = True,
        raise_empty: bool = True,
        xsd: bool = False
) -> Tuple[Dict[str, FileLog], bool]:
    """ Tests all single files in files and returns their filelog as well as a global boolean status

    """
    statuses: Dict[str, FileLog] = defaultdict(FileLog)

    if format == "alto":
        cls = AltoXML
    elif format == "page":
        cls = PageXML

    for file_name in files:
        parsed_xml = None

        # For some tests, we need to parse the file internally
        if segmonto or check_empty:
            obj = cls(file_name)
            parsed_xml = obj.xml

            zone_errors, line_errors, empty = obj.test(check_empty=check_empty, test_segmonto=segmonto)

            if segmonto:
                statuses[file_name].append(
                    Status(
                        "success" if not zone_errors else "failure",
                        task="segmonto",
                        message=f"{len(zone_errors)} wrongly tagged zones" if zone_errors else "",
                        errors=parse_segmonto_errors(zone_errors, group=group, element_type="zone"),
                        level="zone"
                    )
                )
                statuses[file_name].append(
                    Status(
                        "success" if not line_errors else "failure",
                        task="segmonto",
                        message=f"{len(line_errors)} wrongly tagged lines" if line_errors else "",
                        errors=parse_segmonto_errors(line_errors, group=group, element_type="line"),
                        level="line"
                    )
                )

            if check_empty:
                empty = parse_empty(empty, group=group)

                for results, element_type in zip(empty, ["zone", "line"]):
                    if not results:
                        success = "success"
                    elif raise_empty and results:
                        success = "failure"
                    else:
                        success = "warning"

                    statuses[file_name].append(
                        Status(
                            success,
                            task="empty-verification",
                            message=f"{len(results)} empty {element_type}(s) found" if results else "",
                            errors=results,
                            level=element_type
                        )
                    )
        if xsd:
            validator = Validator(Validator.retrieve_xsd(parsed_xml if parsed_xml is not None else file_name))
            if validator.validate(file_name):
                statuses[file_name].append(Status("success", task="schema", message="validation passed"))
            else:
                statuses[file_name].append(
                    Status(
                        "failure",
                        task="schema",
                        message="validation failed",
                        errors=parse_alto_logs(validator.xmlschema.error_log, group=group)
                    )
                )

        if verbose:
            filelog = statuses[file_name]
            passed, total = filelog.score
            status_string: str = "success" if passed == total else "failure"
            # Print the element overal status
            click.echo(click.style(f"{_char(status_string)} [{passed}/{total}] {file_name}", fg=_color(status_string)))
            # Print the details
            filelog.print()

    passing_files = [int(bool(file_statuses)) for file_statuses in statuses.values()]

    if verbose:
        click.echo("\n\n\n=====\nREPORT\n=====\n")
        click.echo(f"{sum(passing_files)}/{len(statuses)} valid XML files")

    return statuses, len(statuses) == sum(passing_files)

