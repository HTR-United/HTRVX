import sys
import click

from htrvx.testing import apply_tests


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option("-v", "--verbose", default=False, is_flag=True,
              help="Prints more information", show_default=True)
@click.option("-f", "--format", default="alto", type=click.Choice(["alto", "page", "auto"]),
              help="Format of files", show_default=True)
@click.option("-s", "--segmonto", is_flag=True, default=False,
              help="Apply Segmonto Zoning verification", show_default=True)
@click.option("-e", "--check-empty", is_flag=True, default=False,
              help="Check for empty lines or empty zones", show_default=True)
@click.option("-r", "--raise-empty", is_flag=True, default=False,
              help="Warns but not fails if empty lines or empty zones are found", show_default=True)
@click.option("-x", "--xsd", is_flag=True, default=False,
              help="Apply XSD Schema verification", show_default=True)
@click.option("-g", "--group", default=False, is_flag=True, help="Group error types")
def cmd(files, verbose: bool = False, group: bool = True, format: str ="alto", segmonto: bool = True,
        check_empty: bool = True, raise_empty: bool = True,
        xsd: bool = False):
    """ Apply the XSD on FILES. XSD can be a URI, a filepath or a schema provided with this tool (eg. "ALTO-Segmonto")

    eg. `htrvx ./data/**/*.xml --group --schema --format alto`

    """
    if apply_tests(files, verbose=verbose, group=group, format=format, segmonto=segmonto,
                   xsd=xsd, raise_empty=raise_empty, check_empty=check_empty):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    cmd()
