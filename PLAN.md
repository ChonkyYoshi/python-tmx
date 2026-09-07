# Hypomnema v2 plan

Hypomnema v2 is a typed Python library being built for reading, creating,
transforming, and writing TMX 1.4b translation memories. The target is a
streaming, lxml-only library with hardened parsing, structural validation
against a bundled DTD, and Pydantic domain models.

This document is a guidepost, not the TMX specification. It records the agreed
direction and identifies what is still pending. Except for the current-state
section, API examples and behavior below describe the target, not functionality
that necessarily exists yet.

Sources of truth:

- [TMX 1.4b specification](src/hypomnema/resources/Spec-TMX-1.4b.md), converted
  from the official GALA publication: value semantics, prose requirements,
  recommendations, and examples. The DTD is not a substitute for this text.
- [Bundled DTD](src/hypomnema/resources/tmx14.dtd): element/attribute inventory
  and XML content models. Do not duplicate that inventory in this plan.
- [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646.html), sections 2.1 and
  2.2.9: language-tag grammar and well-formedness versus validity.
- [GAPS.md](GAPS.md): review context, decisions, and remaining questions.
  Agreed decisions are incorporated here; unresolved details stay explicit.

## Current implementation and verification

- **Project shell exists.** Python 3.14 minimum; runtime dependencies are lxml
  and Pydantic. The dev group contains pytest, Ruff, ty, and types-lxml.
  `ruff.toml` currently sets two-space indentation and 120-character lines.
- **`bcp47.py` is implemented and tested.** It checks RFC 5646 ABNF
  well-formedness, not registry validity. Non-ASCII input is rejected before
  case conversion, including Kelvin-sign lookalikes. `tests/test_bcp47.py`
  covers RFC examples, all grandfathered literals, grammar boundaries,
  malformed input, and API behavior. The last recorded run passed 529 cases;
  the suite is under review.
- **`validators.py` and `models.py` are implemented but not yet tested.**
  They still need the agreed changes: native unsigned-number enforcement,
  validation-error causes, Python-native dumps, datetime offset/precision
  preservation, explicit union discrimination, model cardinality constraints,
  separate TU metadata/variants, and consistent language validation/warnings.
  Current datetime code still truncates microseconds and writes UTC; current
  unions are ordinary unions. These are pending changes, not the contract.
- **XML/I/O are not implemented.** `io.py`, the modules in `xml/`, and the
  public facade in `__init__.py` are placeholders. `errors.py` currently
  defines only `TmxWarning`, used for unknown encoding-name advisories.
  Whole-tree validation APIs and the prose-rule audit are also pending.
- **Some XML experiments exist.** `spike/` contains detached-fragment DTD
  validation, DTD cost, and `xmlfile` lifecycle/buffering experiments. These
  are not an automated conformance suite or proof of end-to-end streaming
  safety, memory bounds, or performance.
- **Testing infrastructure is minimal.** `pytest.toml` discovers `tests/`,
  uses importlib import mode, and enables strict configuration/marker checks.
  No coverage or property-testing dependencies, CI configuration, or
  XML/model/value test suites have been added.
- **Resources are present in the checkout.** DTD inclusion in a built wheel
  and loading through package resources outside the checkout still need
  verification. The README/facade have not been brought up to date for v2.

## Hard constraints

- lxml is the only XML layer. No backend abstraction, no stdlib
  `ElementTree` compatibility.
- Pydantic models are the public domain objects. They own value validation
  and selected structural constraints; explicit broader validation handles
  rules involving a tree rather than one locally assigned field.
- Streaming is the primary document API. The target memory bound is the
  header plus the largest single translation unit, independent of unit count.
- The supported vocabulary is TMX 1.4b and nothing else. Deprecated
  constructs (`<ude>`, `<map>`, `<ut>`, legacy `lang`, `srclang="*all*"`) are
  modeled; vendor extensions are rejected. Value-policy boundaries, such as
  the datetime parser's supported repertoire, are stated below.
- Strict is the only read policy. Unknown elements or attributes, invalid
  content models, malformed values, and broken document structure are errors.
- Successfully completed writer output must be spec-compliant TMX. This
  does not promise meaningful translations or completeness beyond the TMX
  requirements, nor intact output after an interrupted write or I/O failure.
- Python 3.14 minimum. Gates: `uv run ty check`, Ruff, and `uv run pytest`.
  Dependencies move through `uv` only.

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
  Semantic text and modeled structure are; datetime offsets and supported
  fractional precision are retained, not normalized away.
- A full ISO 8601 parser or arbitrary-precision timestamps beyond Python's
  `datetime` representation.
- Parent tracking, cascading validation on child mutation, or a guarantee
  that failed assignments roll back all changes.

## Strictness has three layers

Keep validation out of the projection machinery: plans describe XML mapping,
not a second schema language. Some overlap between models and the DTD is
intentional; independence is useful when it catches drift.

1. **XML safety and well-formedness:** a hardened lxml parser configuration.
   Malformed XML is `TmxParseError`. Untrusted input declarations must not
   gain authority or cause external-resource access; internal-subset behavior
   remains an explicit parser-security question below.
2. **TMX structure:** a bundled, trusted `tmx14.dtd` validates each completed
   `<header>` and `<tu>` before model conversion. The reader separately
   enforces document order: one `<tmx version="1.4">`, one `<header>`, one
   `<body>`, only `<tu>` children. Models also reject structurally invalid
   construction, such as missing required children, and encode legal groups
   rather than letting callers construct arbitrary child orderings.
3. **Domain and prose rules:** Pydantic validators own values such as
   datetimes, integers, language tags, and prose enums such as `assoc`.
   Broader validators handle relationships such as `<ude base>` being
   required when a child `<map>` carries `code`. These checks must be
   available to callers and invoked by the writer; strict reading must also
   enforce the applicable rules on consumed data. Their exact API and scope
   will be settled during the prose audit.

Namespaces: TMX 1.4b is namespace-free, so strict input is too. Foreign
namespaces are not matched by local name, since that would let another
vocabulary impersonate TMX. `xml:lang` is the one predefined-namespace
exception.

Comments and processing instructions are XML syntax, not TMX domain data. The
reader accepts and discards them and keeps their tails: `a<!--c-->b` reads as
`ab`.

## Architecture

Target responsibilities, with current placeholders identified above:

```text
src/hypomnema/
  __init__.py    public facade and __all__
  errors.py      error hierarchy and TmxWarning
  bcp47.py       standalone RFC 5646 grammar validation (stdlib only)
  validators.py enums, Annotated value aliases, parse/format functions
  models.py     all Pydantic TMX models (recursive family, one module)
  xml/
    dtd.py      loads and caches the bundled DTD
    plans.py    hardcoded per-model projection plans
    content.py  the one implementation of text/child/tail interleave
    parse.py    element -> model walker
    build.py    model -> element walker
  io.py         TmxReader, TmxWriter, HeaderPeek
  resources/
    tmx14.dtd
    Spec-TMX-1.4b.md
```

Dependencies point one way: errors and the independent BCP 47 module, then
validators, then models, then XML, then I/O. `models.py` never imports lxml.
The location and public entry points of broader domain validation are still
to be designed; do not invent a module/framework before the rules are audited.

## Models

The target shared base configuration is:

```python
class TmxModel(BaseModel):
  model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True, validation_error_cause=True)
```

Deliberate `BeforeValidator` functions perform the few conversions we mean to
allow; nothing inherits Pydantic's loose coercion by accident. Error-cause
configuration still needs to be added to the implemented base.

### Shape and ordering

- Repeated fields are tuples. A shared validator accepts lists or tuples on
  input and stores tuples. This prevents unchecked list mutation, while
  `model.items += (value,)` rebinds and undergoes assignment validation.
- Metadata that can interleave stays interleaved. Never split notes from
  properties: use one ordered `Note | Property` tuple. The header retains
  its ordered `Note | Property | Ude` children.
- A translation unit has a metadata tuple and a separate **nonempty** variant
  tuple. Write metadata first, then variants, preserving each group's order.
  This matches `(note|prop)*, tuv+`; there is no legal interleaving across
  those groups to preserve. Final field names for the split are not decided.
- A variant likewise keeps metadata separate from segment content, as the
  current model already does. There is no `Segment` model: `<seg>` has no
  attributes or identity and is written around the variant's content tuple.
  Empty segment content is legal.
- Reject structurally invalid construction. `TranslationUnit()` without
  variants and `Ude(name="example")` without maps are errors in the target
  design, not construction states deferred to the writer's DTD check.
- Two inline-content grammars, exactly as the DTD says: `seg`/`hi`/`sub` take
  general inline content; paired and placeholder tags take text plus `<sub>`
  only. One shared union would accept illegal nesting.
- Field names are mechanical: the spec attribute with `-` and `:` replaced
  by `_`. So `o_tmf`, `xml_lang`, and otherwise verbatim, including `type`,
  `i`, and `x`. Class names stay descriptive (`TranslationUnit`, not `Tu`).

A representative node skeleton, unchanged in shape by the union decision:

```python
class Bpt(TmxModel):
  element: Literal["bpt"] = Field(default="bpt", frozen=True)
  i: TMXInteger
  x: TMXInteger | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()
```

### Tagged input and JSON

Every node has a defaulted, frozen `element: Literal["..."]`. It identifies
the XML tag and the JSON node type. Explicit model constructors are the
preferred Python interface: `Hi()` already identifies its class, and callers
do not have to repeat the tag. The same applies to direct
`Hi.model_validate(...)` and already-typed instances in content sequences.

At a slot choosing between multiple model types, dictionaries/JSON must
supply `element`. Configure **explicit discriminated unions**; reject missing
or unknown tags rather than guessing from field shape. The current ordinary
unions have overlapping shapes and need this change.

Mixed content remains ordinary strings plus a tagged model-only union:

```python
type InlineNode = Annotated[Bpt | Ept | Ph | It | Hi | Ut, Field(discriminator="element")]
type SegContentItem = str | InlineNode
```

Attach the discriminator to the model union, not to the surrounding
string/node union. No extra tag requirement is needed where the model type
is unambiguous, such as the `Sub` branch of `str | Sub`.

Tagged JSON preserves modeled node identity, so a dumped `<hi>` cannot
revalidate as `<ph>`. It is a model representation, not an XML preservation
format. Normal dumps include the tag; deliberately omitting defaulted fields
can remove it and is not the complete round-trip representation.

### Assignment and whole-tree validation

The guarantee is **successful assignment satisfies the model's local
constraints**. Tuples do not make child models immutable. Changing a child
can invalidate a relationship with its parent; no parent tracking or
cascading validation will be added to prevent that. Failed assignment is
not promised to be transactional.

Broader validators must be user-invocable and must run in the writer, in
addition to DTD validation. Do not assume `model_validate(existing_model)`
performs a deep check: Pydantic trusts existing instances by default. The
chosen explicit-validation API must actually recheck the necessary data,
with its implementation and instance-handling policy verified by tests.

## Values and serialization

- **Datetimes:** accept native `datetime` values and date-time strings
  representable and parseable by `datetime.fromisoformat()`. Require both
  date and time, rejecting date-only strings even though that parser accepts
  them. Do not impose the current code's narrower `T`/`t` separator requirement;
  date-time syntax follows `fromisoformat()`. Reject standalone `date`/`time`
  objects, unrelated strings, and other input types. This is a deliberately
  bounded Python datetime policy, not a claim to implement all ISO 8601 forms.
- **Datetime preservation:** assume UTC when no timezone is provided.
  Otherwise retain the supplied timezone/offset in the model and its offset
  in JSON/XML output; do not force UTC. Preserve fractional seconds to
  `datetime`'s microsecond precision, with no truncation to whole seconds.
  Exact lexical spelling, arbitrary sub-microsecond precision, and a named
  timezone's Python identity in serialized text are not promised. The
  spec's basic UTC timestamp pattern is a recommendation, not our required
  output form; final lexical formatting is to be settled in implementation.
- **Decimal integers:** attributes treated as numbers must be unsigned
  integers. Reject negative native integers, booleans, and floats as well as
  signed, whitespace-padded, non-ASCII, or underscore-containing strings.
  Leading zeros are accepted; their spelling need not be retained. This is
  the library's explicit numeric policy, not something the CDATA DTD enforces.
- **Hexadecimal values:** `<map unicode>` and `<map code>` use `#x`-prefixed
  hex strings or native unsigned integers, with no booleans or floats.
  Unicode code points must be Unicode scalar values (0 through `0x10FFFF`,
  excluding surrogates, including private-use areas). Formatting keeps the
  `#x` prefix and hexadecimal digits rather than decimalizing the value.
- **Languages:** RFC 5646 ABNF well-formedness, not registry membership or
  other validity rules. Duplicate variants and extension singletons remain
  well-formed and are accepted. Tags are ASCII and case-insensitive, with
  their spelling preserved. `srclang` also accepts `*all*`, normalizing its
  case to that spelling. Registry checks can become an opt-in later.
- **Other values:** enums where the DTD or prose defines them (`segtype`,
  `pos`, `assoc`); whitespace-free `tuid`; ASCII `map ent` and `map subst`.
  Encoding names describe source material and stay strings, not Python
  codec objects. Unknown names produce a soft warning rather than rejection.

Value aliases use public Pydantic functional metadata (`BeforeValidator`,
`AfterValidator`, `PlainSerializer`) so a `TMXDatetime` is honestly a
`datetime`. Python-mode `model_dump()` retains native values for integer,
hexadecimal, and datetime aliases. JSON and XML use their string formatters,
sharing one formatter per value type; serializers must not turn Python-mode
dumps into strings. XML output still goes directly from model fields to the
projection walker rather than through `model_dump()`.

### Deprecated language attributes and warnings

`lang` is deprecated; `xml_lang` is the standard field for `xml:lang`.
Validate both as language tags, with these policies:

- A variant requires `xml_lang`; legacy `lang` cannot substitute for it.
- Notes and properties may omit either or both attributes. Legacy `lang`
  without `xml_lang` is accepted with a warning: technically correct, but
  deprecated; use `xml:lang` if possible.
- If both attributes differ, warn rather than reject. Compare
  case-insensitively, so `en-US` and `EN-us` do not conflict. Run advisory
  checks on validation/assignment and writer validation.
- Never synthesize one attribute from the other. If only `xml_lang` is
  supplied, `lang` remains `None` and is omitted from XML.

Warnings use `TmxWarning`, allowing callers to filter or escalate advisories.
The existing encoding-name warning is the first implemented use; language
advisories still need implementation.

## Prose-rule audit

Before claiming full strictness, audit the complete TMX spec, not only its
DTD. Mandatory requirements become validation rules. Recommendations may
warrant warnings when actionable; examples and conventions must not become
requirements merely because the spec illustrates them.

Known broader rules include `Ude.base` when a child map has `code`, paired
`bpt`/`ept` identifiers, and unique `bpt.i` values within a segment. The spec
permits overlapping native code pairs, so an XML-style stack-nesting check
would be wrong. Scope across nested `hi`/`sub` content and the placement/API
of checks remain to be settled during the audit. No claim is made that this
short list is exhaustive or that those validators already exist.

## Projection: hardcoded plans

TMX 1.4b is frozen, so the model-to-XML mapping is data, not something to
derive. `xml/plans.py` hardcodes one immutable plan per model: the element
name, ordered attribute rows, and the content shape (plain text, ordered
child groups with tag dispatch maps, mixed inline content, or wrapped mixed
content like `<seg>`). The mechanical naming rule makes attribute field
names computable, so an attribute row is little more than the XML attribute
name and a formatter.

There is deliberately no marker system and no introspection-based plan
compiler. A compiler for one program that never changes is generic machinery
with a single client. The safeguard replacing it is testing built from the
DTD itself: tests parse the bundled DTD and assert that plans, models, and
DTD agree in both directions. Every declared attribute and content slot is
covered, and nothing is covered that is not declared, accounting explicitly
for wrappers such as `<seg>`. Drift fails a named test, not a customer file.

Two generic walkers execute plans. `from_element` goes element to model,
ends in `model_validate`, and surfaces `ValidationError` as `TmxSpecError`
with element and line context. Strict consumption also invokes applicable
broader domain checks. `to_element` goes model to element for the writer,
which performs domain checks and DTD-validates the output before committing
bytes. Plans map fields to XML mechanics; they do not own validation rules.
Models encode required structure and groups, while the DTD independently
checks the resulting order, cardinality, and attributes.

`content.py` is the only code that touches lxml's text/tail mechanics, in
both directions. Earlier experiments exposed how easily sharing incorrect
interleave logic can make round-trip checks pass vacuously.

Text normalization at this boundary is still open (GAPS #9): `None` versus
empty text, adjacent/empty strings in mixed content, semantic round-trip
equality, and the rejection boundary for XML-illegal characters. Do not
settle these by quietly stripping whitespace or equating literal XML text
with a textual `map unicode="#x..."` attribute.

## Parser security

Input XML is untrusted. The proposed hardened `iterparse` configuration is:

```text
resolve_entities=False   load_dtd=False   attribute_defaults=False
dtd_validation=False     no_network=True  huge_tree=False
```

Only the packaged DTD has schema authority. Input DOCTYPEs are not preserved;
external DTD/resource loading must not occur. The intended reader rejects
unresolved entity nodes in content and does not weaken libxml2 limits with
`huge_tree=True`.

**Internal subsets remain unresolved (GAPS #10).** `load_dtd=False` does not
mean libxml2 ignores all internal declarations. Do not repeat the old claim
that internal subsets are never loaded or treat these flags as a security
proof. At parser implementation time, settle the policy for accepting or
rejecting internal declarations and verify actual behavior with hostile
fixtures: no external-resource access, no untrusted defaults changing modeled
data, and explicit entity handling. This question is deferred, not decided
by the wording of the proposed flags.

## Reader

Planned API:

```python
with TmxReader(path) as reader:
  if reader.header_peek.srclang != "en":
    return
  header = reader.read_header()
  for unit in reader:
    consume(unit)
```

- `header_peek` is a frozen dataclass built from the `<header>` start-event
  attributes, validated through the same `validators.py` functions, available
  without explicitly consuming header children. It lets consumers bail out
  without processing a potentially large header/body. It is not a TMX node
  and never touches projection; missing or invalid header attributes raise
  `TmxSpecError` at `__enter__`. Parser read-ahead must be accounted for when
  verifying early-exit behavior.
- `read_header()` visibly advances the stream through the header children and
  returns the full validated header model. There is no skip path: consuming
  the header must look like the side effect it is.
- Iteration yields one detached `TranslationUnit` at a time. At each `</tu>`
  the reader DTD-validates, converts, applies the relevant domain checks,
  clears the element, and deletes preceding siblings. Target memory is
  O(header + largest TU), constant in unit count.
- One iterator per reader, and it is a plain resumable cursor: `break`,
  `islice`, and raw `next()` are all fine. Lifecycle misuse (iterating before
  `read_header()`, a second iterator, use after close) raises
  `ReaderStateError`.
- Use a manual start/end event loop, not `iterparse(tag="tu")`: tag filtering
  suppresses events but still builds skipped subtrees. Track depth and check
  stray text between body children explicitly, because removed TUs mean no
  complete `<body>` ever exists for the DTD to check.
- Strictness covers what was consumed. Early exit does not validate unread
  bytes.

Paths and binary streams are accepted, text streams rejected. The reader
closes only what it opened. Lifecycle, security, read-ahead, and bounded-memory
claims all await implementation and verification.

## Writer

Planned API:

```python
with TmxWriter(destination, header=header) as writer:
  for unit in units:
    writer.write(unit)
```

- `__enter__` validates the complete header's domain/prose constraints,
  builds it, and DTD-validates it before the destination sees a byte. Then
  lxml's `xmlfile` writes the declaration, optional canonical DOCTYPE
  (`doctype=True` emits `<!DOCTYPE tmx SYSTEM "tmx14.dtd">`, default off),
  root, header, and opening `<body>`.
- `write(unit)` checks the unit's current domain/prose constraints, builds
  one `<tu>`, DTD-validates it, and commits it in a single `xmlfile.write`
  call. Validation cannot trust that a mutable model is still valid merely
  because it was valid at construction. DTD validation alone cannot enforce
  the prose rules.
- A validation failure may be invalid caller data after mutation or a
  model/projection bug; it is not necessarily an internal bug. The current
  lifecycle direction is to fail and stay failed, not silently skip bad
  units. Exact error classification and partial-output behavior will be
  settled and tested with the writer; callers wanting skip-bad-units
  semantics use explicit validation before writing.
- Successfully completed output is spec-compliant TMX. The writer must check
  all applicable document-level as well as fragment-level rules identified
  by the audit; per-TU DTD success is not by itself proof of this guarantee.
- Output is namespace-free, UTF-8 by default. Input encoding never leaks into
  output decisions. Datetime offsets/precision are modeled values, unlike
  the input document's transport encoding, and are retained.
- Streaming output is not transactional. With a usable destination, cleanup
  may close scopes around a successfully written prefix, but exceptions,
  interrupted writes, or I/O failures can leave partial output. No blanket
  well-formedness/compliance promise covers failed writes. Callers needing
  all-or-nothing output write to a temporary path and rename on success.

## Errors

Planned TMX error hierarchy:

```text
TmxError
├── TmxParseError      bytes are not usable XML
├── TmxSpecError       data violates the TMX contract
├── ReaderStateError   reader lifecycle misuse
└── WriterStateError   writer lifecycle misuse
```

`except TmxError` catches everything the I/O APIs raise about TMX itself.
`OSError` and system exceptions propagate untouched. Direct model validation
of rejected user input raises Pydantic `ValidationError`, preserving its
field locations and aggregated detail rather than replacing it with a custom
wrapper.

Enable `validation_error_cause=True` for underlying exceptions to appear as
an exception-group cause where applicable. This does not make Pydantic catch
validator `TypeError`s: deliberately report bad user input through supported
validation errors and preserve translated causes without broadly catching
programming mistakes or manufacturing a `TypeError` for every rejection.

The standalone BCP 47 API remains distinct: its predicate returns false for
non-string input; its raising validator raises `TypeError` for non-strings
and `ValueError` for malformed tags.

`TmxWarning(UserWarning)` is a separate advisory category, not part of the
error hierarchy. It already exists; the TMX exception classes do not yet.

## Testing

Tests live under root `tests/`. Start with flat modules (`test_bcp47.py`, then
`test_validators.py` and `test_models.py`); introduce an XML subtree when there
is XML code to test. Use plain test functions, parametrized input/expected
examples, and inline setup. Shared fixtures are for genuinely shared needs,
not a prerequisite for creating a model.

- **Grammar:** derive expectations from the RFC independently of the
  implementation's tables. This is the first implemented test slice.
- **Values:** exercise parse/format functions and strict Pydantic aliases,
  including native inputs, error boundaries, warnings, and both Python and
  JSON serialization. Assert expected values, not only self-round-trips.
- **Models:** lock down tuple behavior, explicit discrimination, recursion,
  cardinality, metadata order, assignment boundaries, and tagged JSON.
  Broader-rule tests follow the prose audit and chosen validation API.
- **Projection:** hand-authored XML to expected models, hand-authored models
  to expected XML structure/text, and additional round trips. Reader/writer
  agreement alone is not an independent oracle. Include DTD-derived
  agreement tests and exact mixed-content/whitespace assertions.
- **I/O:** lifecycle, stream ownership, error context, malicious XML,
  document structure, and bounded memory once implemented. Small security
  tests run normally; genuinely expensive memory/performance checks may be
  separately marked. Include native lxml allocations in memory measurements,
  not only Python allocations.
- **Packaging:** verify the bundled DTD in a built wheel and load it via
  package resources outside the source checkout.

`uv run pytest` runs every current test by default. No mocks are needed for
the existing grammar suite. Coverage and property-based testing may be useful
later, but no dependencies or coverage target have been adopted. Existing
spike scripts remain experiments, not substitutes for assertions in the suite.

## Performance posture

Keep the earlier experimental design conclusions, and re-measure when a
real decision depends on them rather than treating historical results as
verified performance of the current placeholders:

- Plain Pydantic validation is the default. `model_construct` is not a
  validation-bypassing optimization strategy.
- XML output goes model, plan, element. `model_dump()` in the middle adds
  allocations without serving the projection design.
- Streaming, not weaker validation, is the answer to memory.
- Benchmarks need an independent oracle (expected XML plus DTD validation
  plus read-back), and compared implementations must not share the algorithm
  under test. Shared mixed-content bugs can make equivalence checks pass
  vacuously.
- A per-fragment DTD cost spike exists. Measure validation's cost in the
  first actual end-to-end streaming benchmark before optimizing anything;
  there is no current integrated pipeline to benchmark yet.

## Roads deliberately not taken

- XML backend abstraction: one client, pure overhead.
- `model_dump()`-based XML output: adds an unnecessary intermediate form.
- Introspection-based projection compiler: replaced by hardcoded plans plus
  DTD-derived agreement tests.
- Separate note/prop lists: reorders valid documents. Separating a TU's
  metadata from its variants is different and matches the DTD's groups.
- One universal inline union: accepts DTD-illegal nesting.
- Inferring node identity from dictionary shape: require explicit tags at
  heterogeneous model slots instead.
- Registry language validation by default: validity is not well-formedness.
- Forced UTC conversion or second-only timestamps: retain supplied offsets
  and supported fractional precision instead.
- Automatic parent revalidation on child mutation: use local assignment
  checks and explicit broader validation, with the writer as final boundary.
- Preserving input DOCTYPEs, transport encodings, or timestamp spellings:
  lexical/transport facts are not the preservation contract.

## Sequence from here

Work create, then test, then document, per piece, with review between stages.
Do not turn pending decisions or known gaps into passing tests that bless
accidental current behavior.

1. **Review the BCP 47 test slice.** Implementation and 529 passing cases are
   in place; this is the current testing frontier.
2. **Bring values into line with the decisions above.** Unsigned native
   inputs, error causes, datetime input bounds/offsets/fractions, and separate
   Python versus JSON serialization. Review the changes, then lock them down
   with `test_validators.py`.
3. **Bring model shape into line.** Explicit discriminators, TU grouping,
   nonempty required children, consistent language values/advisories, and
   assignment guarantees. Settle final field names, review, then test the
   recursive models and their serialization contracts.
4. **Audit the full TMX prose and design broader validation.** Decide scope
   and public entry points, implement the required checks, then test them.
   Recommendations and warning choices get their own review; the DTD alone
   does not determine this work.
5. **Build projection.** DTD resource loader, hardcoded plans, shared content
   interleave, and walkers. Resolve GAPS #9's XML/text boundary questions,
   verify recursive discriminated aliases on the real shapes, and add DTD
   agreement and independent-oracle tests after review.
6. **Build reader and writer.** Revisit the existing XML spikes, resolve
   GAPS #10's internal-subset/entity policy, and verify hardened parsing,
   validate-before-commit, lifecycle, domain conformance, and bounded memory.
   Then add the corresponding I/O suite and end-to-end streaming benchmark.
7. **Finish distribution and public surface.** Verify wheel resources, add
   the facade/`__all__`, update the README, and document the settled API and
   guarantees. CI and any additional test tooling can be chosen when needed.

A failed spike changes this plan, not an excuse to silently weaken the
agreed validation or safety contract.
