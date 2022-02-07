import sys
import click

from htrvx.schemas import apply_tests


@click.command()
@click.argument("xsd")
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option("-v", "--verbose", default=False, is_flag=True)
@click.option("-g", "--group", default=False, is_flag=True, help="Group error types")
def cmd(xsd, files, verbose: bool = False, group: bool = True):
    """ Apply the XSD on FILES. XSD can be a URI, a filepath or a schema provided with this tool (eg. "ALTO-Segmonto")

    eg. `htrvx ALTO-Segmonto ./data/**/*.xml --group`

    """
    if apply_tests(xsd, files, verbose, group):
        sys.exit(1)
    else:
        sys.exit(0)
