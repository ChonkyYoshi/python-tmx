# Python-tmx
A python library based on lxml to help create, edit, and export tmx files quickly.

# Installation
Install the latest version of the library using Pypi, note that lxml is required.
```python
pip install -U python-tmx
```
# How to use
## Basics
A tmx file is represented as a `tmx` object, containing a `header` and a list of `tu` object. Each tu is then further divided into `tuv` objects, each having a list of `run` object representing text and the different tags available.
Further, `header`, `tu` and `tuv` objects all have a list of `note` and `prop` objects.

Every possible attribute defined by the spec is represented by an attibute of that object accesible using dot notation. so for example, if you want to change the 'creationtool' attribute of a tmx header you can simply do the following:
```python
tmx_file.header.creationtool = "python-tmx"
```
## Simple Usage
The below snippet shocases how to make a multilingual tmx bilingual with very little effort
```python
from tmx.structural import tmx
from tmx import load_tmx

tmx_file: tmx = load_tmx("tmx-file.tmx")  # Load a tmx file into memory
for tu in tmx_file.tus:  # loop through all tus
    for index, tuv in enumerate(tu.tuvs):  # loop through all tuv
        if tuv.xmllang not in ["en-US", "fr-FR"]:  # check tuv language
            tu.tuvs.pop(index)  # remove tuv if not english or french
tmx_file.export("new-tmx.tmx")  # export now bilingual tmx object into a tmx file
```
