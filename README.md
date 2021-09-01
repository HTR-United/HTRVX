# HTRVX : HTR Validation with XSD

HTRVX - pronunced Ashterux - allows for simple XSD control of your corpora. Use remote XSDs, local ones or simply the one package with the repository.

Currently available XSDs:

- ALTO-Segmonto: Segmonto ontology + Alto

## How to install

Simply run `pip install htrvx`

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
        htrvx --verbose --group ALTO-Segmonto UNIX/Path/to/**/your/*.xml

```