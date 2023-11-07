# Python-tmx
A python library based on lxml to help create, edit, and export tmx files quickly.

# Installation
Install the latest version of the library using Pypi
```python
pip install -U python-tmx
```
# How to use
## Basics
> [!Note]
> This readme will assume you're not familiar with the inner structure of a tmx and the different attributes of each tag.

The library represents a tmx file and its various parts as objects.

As such, a tmx file becomes `tmx` object, containing a `header` and a list of `tu` object. Each tu is then further divided into `tuv` objects, each having a list of `run` object representing text and the different tags available.

### The header
The header object contains no text, only a few different attributes, some required, and some optional:
- Required attributes:
    
    creationtool, creationtoolversion, segtype, o-tmf, adminlang, srclang, datatype.
- Optional attributes:
    
    o-encoding, creationdate, creationid, changedate, changeid

**Remark:** while you can create an empty header object without specifying any of the 