<img src="./img/htrvx.png" width=300 align=right>

# HTRVX : HTR Validation for eXtra-quality controlled documents

[![Test library](https://github.com/HTR-United/HTRVX/actions/workflows/test.yml/badge.svg)](https://github.com/HTR-United/HTRVX/actions/workflows/test.yml)

HTRVX - pronounced Ashterux - allows for quality control of XML using XSD schema validation, Segmonto validation and other verifications. 

## How to install

Simply run `pip install htrvx`

## How to run

The basic way to run the script is `htrvx PATHTOFILES --format FORMAT`, eg. `htrvx ./tests/test_data/page/*.xml --format page`

Each verification is an opt-in verification: you need to express the fact that you want to check it.

- `--segmonto` will check for Segmonto compliancy
  - You can use your own vocabulary or a restricted Segmonto vocabulary by using `--zone ZONENAME` and `--line LINENAME` such as `htrvx [...] --line DefaultLine --line HeadingLine --zone MainZone`
- `--xsd` will check if the data are compliant with XML Schemas
- `--check-empty` will check if regions have no lines or if lines have no text
    - `--check-empty` can be refined with `--raise-empty` to throw an error if empty elements are found, otherwise it's simply reported.
= `--check-image` checks for link in the XML. Link are checked relatively to the XML file, ie. if XML file ./data/element.xml points to file.jpeg, file ./data/file.jpeg is expected to exist.

Other parameters mainly have to do with verbosity: `--verbose` displays details about errors, `--group` groups errors (instead of showing one line per error, groups by error types).

| Parameters               | Default | Function                                                                                 |
|--------------------------|---------|------------------------------------------------------------------------------------------|
| -v, --verbose            | False   | Prints more information                                                                  |
| -f, --format [alto,page] | alto    | Format of files                                                                          |
| -s, --segmonto           | False   | Apply Segmonto Zoning verification                                                       |
| -e, --check-empty        | False   | Check for empty lines or empty zones                                                     |
| -r, --raise-empty        | False   | Warns but not fails if empty lines or empty zones are found                              |
| -x, --xsd                | False   | Apply XSD Schema verification                                                            |
| -g, --group              | False   | Group error types (reduce verbosity)                                                     |
| -i, --check-image        | False   | Check if the image link in the XML points to the right path                              |
| -l, --verbose-level      | zen     | Level of details and amount of color shown in the logs (see [below](#verbosity-levels)). |
| --zone TEXT              | None    | Provide a custom zone to control zone types instead of Segmonto                          |
| --line TEXT              | None    | Provide a custom line to control Line types instead of Segmonto                          |

### Verbosity levels

- `minimal`: shows only failing tests, no details.
- `low`: shows only failing test and their details, such as which lines fails in a file.
- `zen` (default): shows all tests and their details, but displays only one color (red for errors).
- `all`: shows everything.

## Github Action code

If you want to add this to your github repository, as a continuous integration workflow, add a file `htrux.yml` at in the path `.github/workflows` of your repository.


```yaml
# This workflow will install Python dependencies, run tests and lint with a single version of Python
# For more information see: https://help.github.com/actions/language-and-framework-guides/using-python-with-github-actions

name: HTRVX

on: [push, pull_request] # You can edit this of course !

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 3.8
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install htrvx
    - name: Run HTRVX
      run: |
        htrvx --verbose --group --format alto --segmonto --xsd --check-empty --raise-empty UNIX/Path/to/**/your/*.xml

```

---

Logo by [Alix Chagué](https://alix-tz.github.io).
