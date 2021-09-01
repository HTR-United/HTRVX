# HTRVX : HTR Validation with XSD

## How to install

Simply run `pip install htrvx`

## Github Action code

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