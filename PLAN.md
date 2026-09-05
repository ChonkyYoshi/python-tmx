# Hypomnema v2 plan

Hypomnema is a typed Python library for reading, creating, transforming, and
writing TMX 1.4b translation memories. V2 is a rewrite: a streaming, lxml-only
library with hardened parsing, structural validation against a bundled DTD,
and Pydantic domain models.

This document is a guidepost, not a spec. It settles direction and rationale;
everything it leaves open is discovered by building one piece at a time and
checking against the bundled DTD and the TMX 1.4b specification. Element and
attribute inventories in particular are deliberately absent, the DTD already
states them.

## Hard constraints

- lxml is the only XML layer. No backend abstraction, no stdlib
  `ElementTree` compatibility.
- Pydantic models are the public domain objects and own all value validation.
- Streaming is the primary document API. A 500 MB file streams with memory
  bounded by the header plus the largest single translation unit.
- The supported format is all of TMX 1.4b and nothing else. Deprecated
  constructs (`<ude>`, `<map>`, `<ut>`, legacy `lang`, `srclang="*all*"`) are
  modeled; vendor extensions are rejected.
- Strict is the only read policy. Unknown elements or attributes, invalid
  content models, malformed values, broken document structure: all errors.
- Python 3.14 minimum. Gates: `ty check`, Ruff, pytest. Two-space indentation,
  100-character lines. Dependencies move through `uv` only.

## Out of scope

- Vendor dialects and extension elements.
- Lenient skip/preserve/normalize modes. No mode flag ships until a
  non-strict behavior is actually designed; leniency is not a boolean.
- A whole-document container. The header plus unit iteration is the document
  abstraction; a container would either hoard memory or wrap an iterator.
- `load()`/`dump()` convenience wrappers, v1's `ops/` package (redesigned
  later, against the settled domain), registry-backed language validation.
- Lexical fidelity. Comments, processing instructions, entity spelling,
  attribute order, and original datetime spellings are not preserved.
  Semantic text and modeled structure are.

## Strictness has three layers

Keep them separate. The moment they blur, the projection layer starts growing
into a second, incomplete schema language.

1. XML safety and well-formedness: a hardened lxml parser configuration.
   Malformed XML is `TmxParseError`.
2. TMX structure: a bundled, trusted `tmx14.dtd` validates each completed
   `<header>` and `<tu>` before model conversion. The reader separately
   enforces document order: one `<tmx version="1.4">`, one `<header>`, one
   `<body>`, only `<tu>` children. Input DOCTYPEs are never loaded and carry
   no authority.
3. Domain values: Pydantic validators own what the DTD cannot express:
   datetimes, integers, language tags, prose enums such as `assoc`, and
   cross-field rules such as `<ude base>` being required when a `<map>`
   carries `code`.

Namespaces: TMX 1.4b is namespace-free, so strict input is too. Foreign
namespaces are not matched by local name, since that would let another
vocabulary impersonate TMX. `xml:lang` is the one predefined-namespace
exception.

Comments and processing instructions are XML syntax, not TMX domain data. The
reader accepts and discards them and keeps their tails: `a<!--c-->b` reads as
`ab`.

## Architecture

```text
hypomnema/
  __init__.py    public facade and __all__
  errors.py      error hierarchy
  types.py       enums, Annotated value aliases, parse/format functions
  models.py      all Pydantic TMX models (recursive family, one module)
  xml/
    dtd.py       loads and caches the bundled DTD
    plans.py     hardcoded per-model projection plans
    content.py   the one implementation of text/child/tail interleave
    parse.py     element -> model walker
    build.py     model -> element walker
  io.py          TmxReader, TmxWriter, HeaderPeek
  resources/
    tmx14.dtd
```

Dependencies point one way: errors, then types, then models, then xml, then
io. `models.py` never imports lxml.

## Models

All nodes share one base:

```python
class TmxModel(BaseModel):
  model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)
```

Deliberate `BeforeValidator` functions perform the few conversions we mean to
allow; nothing inherits Pydantic's loose coercion by accident.

The calls that shape everything else:

- Repeated fields are tuples. `validate_assignment` checks
  `model.field = value` but cannot see `model.items.append(value)`; tuples
  close that hole, and `model.items += (value,)` rebinds, so it revalidates.
  A shared validator accepts lists or tuples on input and stores tuples.
- Every node carries a frozen `element: Literal["..."]` field. It is the XML
  tag, the Pydantic union discriminator, and the JSON round-trip tag, one
  field for all three.
- Heterogeneous children stay in one ordered tuple of `Note | Property`
  unions. TMX allows interleaving; separate `notes` and `props` lists would
  reorder valid documents on write.
- Two inline-content grammars, exactly as the DTD says: `seg`/`hi`/`sub` take
  general inline content, the paired and placeholder tags take text plus
  `<sub>` only. One shared union would accept illegal nesting.
- No `Segment` model. `<seg>` has no attributes or identity; it is the
  wrapper written around the variant's content tuple.
- Field names are mechanical: the spec attribute with `-` and `:` replaced by
  `_`. So `o_tmf`, `xml_lang`, and otherwise verbatim, including `type`, `i`,
  and `x`. No translation table to remember or maintain. Document loudly that
  `lang` is the deprecated attribute and `xml_lang` the standard one. Class
  names stay descriptive (`TranslationUnit`, not `Tu`).

A representative skeleton:

```python
class Bpt(TmxModel):
  element: Literal["bpt"] = Field(default="bpt", frozen=True)
  i: TMXInteger
  x: TMXInteger | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()
```

JSON comes free and lossless: unions are discriminated by `element`, so a
dumped `<hi>` cannot revalidate as `<ph>`. JSON is a model representation,
not an XML preservation format.
 
## Values

- Datetimes: the spec requires ISO 8601 and only recommends
  `YYYYMMDDTHHMMSSZ`. Accept any ISO 8601 instant (basic or extended, offset 
  or naive, naive means UTC), reject date-only forms, truncate to whole
  seconds so `datetime.now(UTC)` just works, and always write the canonical
  basic form. Round trips may change datetime bytes; that is lexical change,
  not semantic.
- Integers: strict ASCII decimals. No `int()` conveniences, no `bool`.
- Languages: well-formed BCP 47, not registry membership. `srclang` also
  admits `*all*`. Registry checks can become an opt-in later.
- Enums where the DTD or prose defines them: `segtype`, `pos`, `assoc`.
  Encoding names stay plain strings; they describe the source material, not
  Python codecs.

Value aliases use public Pydantic functional metadata (`BeforeValidator`,
`PlainSerializer`) so `TMXDatetime` is honestly a `datetime`, and XML and
JSON share one formatter per type.

## Projection: hardcoded plans

TMX 1.4b is frozen, so the model-to-XML mapping is data, not something to
derive. `xml/plans.py` hardcodes one immutable plan per model: the element
name, ordered attribute rows, and the content shape (plain text, ordered
children with a tag dispatch map, mixed inline content, or wrapped mixed
content like `<seg>`). The mechanical naming rule makes field names
computable from attribute names, so an attribute row is little more than the
attribute name and a formatter.

There is deliberately no marker system and no introspection-based plan
compiler. A compiler for one program that never changes is generic machinery
with a single client. The safeguard replacing it is testing built from the
DTD itself: tests parse the bundled DTD and assert that plans, models, and
DTD agree in both directions, every declared attribute and content slot is
covered, and nothing is covered that is not declared. Drift fails a named
test, not a customer file.

Two generic walkers execute plans. `from_element` goes element to model,
ends in `model_validate`, and surfaces `ValidationError` as `TmxSpecError`
with element and line context. `to_element` goes model to element for the
writer, which DTD-validates the result before committing bytes. Plans map
fields to XML mechanics only; order, cardinality, and required attributes
belong to the DTD.

`content.py` is the only code that touches lxml's text/tail mechanics, in
both directions. That interleave logic is exactly the kind that goes subtly
wrong when written twice; the first benchmark round proved it.

## Parser security

Input XML is untrusted. `iterparse` runs with:

```text
resolve_entities=False   load_dtd=False   attribute_defaults=False
dtd_validation=False     no_network=True  huge_tree=False
```

The input DOCTYPE, internal subsets included, is never loaded, validated, or
preserved; only the packaged DTD has authority. Unresolved entity nodes in
content are rejected. `huge_tree` stays off: a document that trips libxml2's
limits fails instead of silently weakening protections.

## Reader

```python
with TmxReader(path) as reader:
  if reader.header_peek.srclang != "en":
    return
  header = reader.read_header()
  for unit in reader:
    consume(unit)
```

- `header_peek` is a frozen dataclass built from the `<header>` start-event
  attributes, validated through the same `types.py` functions, available
  before any header child is read. It exists so a consumer can bail out of a
  500 MB file for O(1) cost. It is not a TMX node and never touches
  projection; missing or invalid header attributes raise `TmxSpecError` at
  `__enter__`.
- `read_header()` visibly advances the stream through the header children and
  returns the full header model. There is no skip path: consuming the header
  must look like the side effect it is.
- Iteration yields one detached `TranslationUnit` at a time. At each `</tu>`
  the reader DTD-validates, converts, clears the element, and deletes
  preceding siblings. Memory is O(header + largest TU), constant in unit
  count.
- One iterator per reader, and it is a plain resumable cursor: `break`,
  `islice`, and raw `next()` are all fine. Lifecycle misuse (iterating before
  `read_header()`, a second iterator, use after close) raises
  `ReaderStateError`.
- Use a manual start/end event loop, not `iterparse(tag="tu")`: tag filtering
  suppresses events but still builds the skipped subtrees. Track depth, and
  check stray text between body children explicitly, because removed TUs mean
  no complete `<body>` ever exists for the DTD to check.
- Strictness covers what was consumed. Early exit does not validate unread
  bytes.

Paths and binary streams are accepted, text streams rejected. The reader
closes only what it opened.

## Writer

```python
with TmxWriter(destination, header=header) as writer:
  for unit in units:
    writer.write(unit)
```

- `__enter__` builds and DTD-validates the complete header before the
  destination sees a byte, then lxml's `xmlfile` writes the declaration, the
  optional canonical DOCTYPE (`doctype=True` emits
  `<!DOCTYPE tmx SYSTEM "tmx14.dtd">`, default off), the root, the header,
  and opens `<body>`.
- `write(unit)` builds one `<tu>`, DTD-validates it, and commits it in a
  single `xmlfile.write` call. A validation failure here means a projection
  or model bug, not bad data, so the writer fails and stays failed; callers
  wanting skip-bad-units semantics validate before writing.
- Output is namespace-free, UTF-8 by default. Input encoding never leaks into
  output decisions.
- Streaming output is not transactional. A failure mid-stream generally still
  closes scopes and leaves a well-formed document holding the units written
  so far. Callers needing all-or-nothing write to a temporary path and
  rename.

## Errors

```text
TmxError
├── TmxParseError      bytes are not usable XML
├── TmxSpecError       well-formed XML violating the TMX contract
├── ReaderStateError   reader lifecycle misuse
└── WriterStateError   writer lifecycle misuse
```

`except TmxError` catches everything the I/O APIs raise about TMX itself.
`OSError` and system exceptions propagate untouched. Direct model
construction raises plain Pydantic `ValidationError`; wrapping it would only
bury Pydantic's error detail.

## Performance posture

The spike rounds settled the big questions; keep the conclusions and
re-measure numbers when a decision actually depends on them:

- Plain Pydantic validation is fast enough. `model_construct` is not a
  faster escape hatch.
- XML output goes model, plan, element. `model_dump()` in the middle only
  adds allocations.
- Streaming, not weaker validation, is the answer to memory.
- Benchmarks need an independent oracle (expected XML plus DTD validation
  plus read-back), and compared implementations must not share the algorithm
  under test. The first round had a shared mixed-content bug that made its
  equivalence checks pass vacuously.
- Per-TU DTD validation cost is unmeasured. Measure it in the first
  end-to-end streaming benchmark before optimizing anything.

## Roads deliberately not taken

- XML backend abstraction: one client, pure overhead.
- `model_dump()`-based XML output: measured slower, adds nothing.
- Introspection-based projection compiler: replaced by hardcoded plans plus
  DTD-derived agreement tests.
- Separate note/prop lists: reorders valid documents.
- One universal inline union: accepts DTD-illegal nesting.
- Registry language validation by default: registry validity is not TMX
  validity.
- Preserving input DOCTYPEs, encodings, or datetime spellings: transport
  facts, not domain data.

## Sequence

Work create, then test, then document, per piece, with review between stages.

0. Shell: branch, v2 replaces `src/`, dependencies via `uv`, Python 3.14,
   package the DTD as a resource.
1. Spikes for the load-bearing unknowns: hardened `iterparse` behavior with
   an XXE fixture; DTD validation of detached header/TU fragments; recursive
   discriminated aliases on 3.14; a Pydantic field literally named `type`
   (fallback `type_`); `xmlfile` lifecycle and validate-before-commit; per-TU
   DTD validation cost.
2. `types.py` and `models.py`. Stop for API review.
3. Plans, content interleave, walkers, DTD agreement tests. Stop for review.
4. Reader and writer. Verify bounded memory, then the lifecycle, security,
   malformed-input, and round-trip test suite.
5. Facade, `__all__`, README, documentation.

A failed spike changes this plan, not the strictness contract.
