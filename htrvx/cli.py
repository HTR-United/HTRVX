import sys
import click

from htrvx.testing import test
from typing import Sequence, Optional

@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option("-v", "--verbose", default=False, is_flag=True,
              help="Prints more information", show_default=True)
@click.option("-f", "--format", default="alto", type=click.Choice(["alto", "page", "auto"]),
              help="Format of files", show_default=True)
@click.option("-s", "--segmonto", is_flag=True, default=False,
              help="Apply Segmonto Zoning verification", show_default=True)
@click.option("--zone", default=None, multiple=True,
              help="Provide a custom zone to control zone types instead of Segmonto", show_default=True)
@click.option("--line", default=None, multiple=True,
              help="Provide a custom zone to control lines types instead of Segmonto", show_default=True)
@click.option("-e", "--check-empty", is_flag=True, default=False,
              help="Check for empty lines or empty zones", show_default=True)
@click.option("-i", "--check-image", is_flag=True, default=False,
              help="Check if image links in the XML points to real files", show_default=True)
@click.option("-r", "--raise-empty", is_flag=True, default=False,
              help="Warns but not fails if empty lines or empty zones are found", show_default=True)
@click.option("-x", "--xsd", is_flag=True, default=False,
              help="Apply XSD Schema verification", show_default=True)
@click.option("-l", "--verbose-level", default="zen", type=click.Choice(["minimal", "low", "zen", "all"]),
              help="Verbosity level. Minimal show only failing test, "
                   "zen only displays one color (red), "
                   "low shows failing tests with their debug info, "
                   "all shows everything", show_default=True)
@click.option("-g", "--group", default=False, is_flag=True, help="Group error types")
@click.option("--allow-untagged", default=None, type=click.Choice(["line", "zone", "both"]), show_default=True,
              help="Allow untagged zone, line or both in type checking")
@click.option("--max-untagged-zones", default=-1, type=click.INT, show_default=True,
              help="Maximum number of untagged zones")
@click.option("--max-untagged-lines", default=-1, type=click.INT, show_default=True,
              help="Maximum number of untagged lines")
def cmd(files, verbose: bool = False, group: bool = True, format: str ="alto", segmonto: bool = True,
        check_empty: bool = True, raise_empty: bool = True,
        xsd: bool = False, check_image: bool = False, verbose_level: str = "zen",
        zone: Optional[Sequence[str]] = None, line: Optional[Sequence[str]] = None,
        allow_untagged: Optional[str] = None,
        max_untagged_zones: int = -1,
        max_untagged_lines: int = -1):
    """ Apply the XSD on FILES. XSD can be a URI, a filepath or a schema provided with this tool (eg. "ALTO-Segmonto")

    eg. `htrvx ./data/**/*.xml --group --schema --format alto`

    With multiple zones

    eg. `htrvx ./data/**/*.xml --group --schema --format alto --zone Col --zone Header`

    """
    if allow_untagged == "both":
        allow_untagged = {"line", "zone"}
    if test(files, verbose=verbose, group=group, format=format, segmonto=segmonto,
            xsd=xsd, raise_empty=raise_empty, check_empty=check_empty, check_image=check_image,
            verbose_level=verbose_level, zones=zone, lines=line, allow_untagged=allow_untagged,
            max_untagged_zones=max_untagged_zones, max_untagged_lines=max_untagged_lines)[1]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    cmd()
