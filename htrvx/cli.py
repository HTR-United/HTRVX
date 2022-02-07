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
@click.option("-x", "--xsd", is_flag=True, default=False,
              help="Apply XSD Schema verification", show_default=True)
@click.option("-g", "--group", default=False, is_flag=True, help="Group error types")
def cmd(files, verbose: bool = False, group: bool = True, format: str ="alto", segmonto: bool = True,
        xsd: bool = False):
    """ Apply the XSD on FILES. XSD can be a URI, a filepath or a schema provided with this tool (eg. "ALTO-Segmonto")

    eg. `htrvx ./data/**/*.xml --group --schema --format alto`

    """
    if apply_tests(files, verbose=verbose, group=group, format=format, segmonto=segmonto,
                   xsd=xsd):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    cmd()
