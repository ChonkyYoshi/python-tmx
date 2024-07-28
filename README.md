# Overview

PythonTmx is a Python library that aims to make dealing with tmx files in Python
easier.

Every tmx element from the TMX 1.4b standard is represented (including the
deprecated <ut> element for compatibility).

To create a Tmx Element, you can either create it from scratch and set its
attributes using keyword arguments, or you can also give it a lxml element to
parse and use a base. If you give both an lxml element and keyword arguments
the values parsed from the element will take precedence and the keywords
argument values will be used as a fallback.

# Installing

Simply download from Pypi and install using pip:

```bash
pip install --upgrade PythonTmx
```

# Basic usage

You can create a `Tmx` object by reading a tmx file. From there, you can just
iterate over each tu, and further each tuv, do any processing needed and then
just export it back to another file.

```python
from datetime import UTC, datetime

from PythonTmx import from_tmx
from PythonTmx.inline import Ph

# Create Tmx object from a tmx file
tmx_file = from_tmx("tmx_file.tmx")
# Loop over all Tu
for tu in tmx_file:
    # Set the Tu's source language to English
    tu.srclang = "EN"
    # Loop over all Tuv and check the language
    for tuv in tu.tuvs:
        match tuv.xmllang:
            case "EN":
                # If Tuv is in English, add _English at the end
                tuv.segment.append("_English")
            case "FR":
                # If it's French, add a Ph that says "_French"
                # at the start
                tuv.segment.insert(0, Ph(content="_French"))
            case _:
                # Remove the Tuv otherwise
                tu.tuvs.remove(tuv)
        # Add a prop to the Tuv and set the changedate to today
        tuv.add_prop(type="x-confidential", text="True")
        tuv.changedate = datetime.now(UTC)
    # Remove all notes that don't start with "Hello"
    # and also add a new one and set the changedate to today
    for note in tu.notes:
        if not note.text.startswith("Hello"):
            tu.remove_note(note)
    tu.add_note(text="adding a note here, huge success")
    tu.changedate = datetime.now(UTC)
# Export Tmx to a tmx file and to a csv file
tmx_file.to_tmx("bilingual_tmx_file.tmx")
tmx_file.to_csv("bilingual.csv")
```
