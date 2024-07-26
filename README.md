# Overview

python-tmx is a library meant to make dealing with tmx
(Translation Memory Exchange) files easier and more pythonic than just using
a xml parser.
It is based on lxml under the hood and tries to follow the TMX 1.4b standard as
much as possible.

# Installing

Simply download it from pypi:

```python
pip install -U python-tmx
```

# Basics

Every possible tmx element is represented as an object with the same name but in
Title case (i.e. a <header> is a `Header`, a <tuv> is a `Tuv`...).
Every element inherits from the base `TmxElement` class and thus share the
following methods:

### to_element()

This converts the element into an lxml `_Element` object. If the
element has children it will also recursively call `to_element` on all of those
as well, keeping the hierarchy to return an accurate representation of the element.

For example, calling `to_element` on a `Tu` object will also call `to_element`
on all its `Prop`, `Note` and `Tuv` objects, as well as on any `Prop`, `Note`
and the `Seg` element of those `Tuv`.

### make_xml_attrib()

Called automatically when calling `to_element` this methods will convert an
element's attributes to a dict that can be used by used by lxml.

It will raise an Error if:

- a required attribute has a value of None
- an attribute has a forbidden value
- an attribute has a value of a type that is not a str and not one of the
  currently allowed alternative (see the docs for each object to know the allowed
  types for each attribute)

## Tmx

It is the top most parent object and the only object with a `export_to_file`
method available.

It contains 2 main parts:

- a `Header` object, accesible through the `header` attribute
- a list (or any Mutable Sequence if you wish to use something else)
  of `Tu` objects, accessible through the `tus` attribute

You can iterate over the all `Tu` objects of an element by treating it as an
iterable and using a for loop on it:

```python
import PythonTmx as tmx
tmx_obj:tmx.Tmx = tmx.read_from_file("tmx_file.tmx")
for tu in tmx:
  # do something
# OR
for tu in tmx.iter(Tu):
  # do something
```

## Header
