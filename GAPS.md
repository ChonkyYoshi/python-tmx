# Contracts to settle before the next testing slices

Working review sheet, not a replacement for `PLAN.md` or a list of behavior to
preserve just because the implementation currently does it. Edit the **Decision**
lines directly. These items do not block the independent BCP 47 grammar tests.

Sources of truth:

- [`PLAN.md`](PLAN.md): intended library policy and architecture.
- [TMX 1.4b specification](src/hypomnema/resources/Spec-TMX-1.4b.md): value semantics,
  cross-field requirements, and recommendations that the DTD cannot express.
- [TMX DTD](src/hypomnema/resources/tmx14.dtd): XML attributes and content models.
- [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646.html), sections 2.1 and 2.2.9:
  language-tag syntax and the distinction between well-formedness and validity.

## Values

### 1. Native integers bypass the lexical restrictions

**Observed:** `parse_integer()` rejects negative strings, but passes native
negative integers through. `parse_hex_integer()` does the same. Their aliases
have no nonnegative constraint; `TMXUnicodeCodePoint` separately checks its range.
Both parsers also pass `bool` through, relying on downstream strict validation.

**Proposed direction:** enforce the same numeric domain for Python, XML, and JSON
inputs. Decide whether the standalone parser functions reject booleans themselves
or deliberately rely on their Pydantic aliases. The decimal digit-only policy is
in the plan; the spec describes `i`, `x`, and `usagecount` as numbers, while the
bundled XML DTD uses CDATA, so do not claim the DTD enforces this value policy.

**Decision:** We take the stance that attributes the spec defines as "Numbers"
MUST be valid unsigned integers. So negative ints (even native ones) error,
bool error, leading zeros are fine, floats error as well.

### 2. Validation exception boundary

**Observed:** decimal, hexadecimal, and datetime converters raise `TypeError` for
unsupported Python types. Pydantic does not wrap validator `TypeError` as
`ValidationError`. The plan promises plain Pydantic `ValidationError` for bad
direct model construction and eventual `TmxSpecError` wrapping at the XML boundary.

**Proposed direction:** bad user values reaching models should produce
`ValidationError`, without broadly catching programming errors. Standalone BCP 47
functions have a separate, explicit contract: the predicate returns false for
non-strings; the raising validator raises `TypeError`.

**Decision:** Ideally, I want the error being raised to the user to be a
ValidationError *raised from* a type error, providing both a actionable
trace for debugging AND also being easily catchable by user code.

### 3. Datetime input breadth and serialization modes

**Observed:** `parse_datetime()` delegates to `datetime.fromisoformat()` after
requiring a `T`/`t` somewhere in string input. This is not a complete implementation
of every ISO 8601 form. It preserves input offsets, attaches UTC to naive values,
and truncates microseconds; formatting emits canonical UTC. `PlainSerializer`
currently serializes integer, hex, and datetime aliases to strings in both Python
and JSON dumps, not only JSON.

**Questions:** does “any ISO 8601 instant” mean the subset accepted by this parser,
or a broader explicitly enumerated set? Should `model_dump()` expose native values
and only JSON/XML use strings? Normalization and accepted syntax should be tested
against explicit examples, not just self-round-trips.

**Decision:** `model_dump` in python should expose native values such as actual int,
or datetime. Any actual serialization like json/xml will get strings. On the ISO 8601
question, the code should be updated to ensure *any* ISO 8601 compliant *instant*
specifcially will pass validation, anything should fail, so a date or time object,
a string like Monday or January, and any other object, should fail. If no timezone
info is provided, we assume UTC (and document as such). If one is provided, we keep
the existing one since it's valid (most likely requires ammending the formatting functions).

## Models

### 4. Tagged input and union discrimination

**Observed:** every node has a frozen literal `element` with a default, but the
unions are ordinary Pydantic unions, not explicitly discriminated as the plan says.
Multiple node types have overlapping shapes when the tag is absent (for example,
inline nodes with only optional fields). Dumped JSON carries the tag; hand-authored
nested dictionaries need not.

**Questions:** must nested dictionaries include `element`? Should ambiguous untagged
input be rejected rather than inferred? Keep convenient constructors such as
`Hi()` distinct from the rules for selecting a node type from a union. Mixed
string/node content needs a discrimination approach that still accepts strings.

**Decision:** use explicit `element` discrimination for heterogeneous model unions
(option 2). Node identity comes from the chosen class or an explicit tag, never
from guessing based on field shape.

- Keep `element` defaulted and frozen: constructors such as `Hi()` and direct
  validation through `Hi.model_validate(...)` already identify the class and do
  not require the caller to repeat its tag. Already-typed model instances remain
  accepted in content sequences.
- Dictionaries/JSON in slots choosing between multiple model types must carry
  `element`. Reject missing or unknown tags; do not fall back to inference.
- Mixed content remains ordinary strings plus a tagged model-only union. Attach
  the discriminator to the model union, not to the surrounding string/node union.
- No additional tag requirement where the model type is already unambiguous,
  such as the `Sub` branch of `str | Sub`.

The extra verbosity for hand-authored dictionaries is acceptable; explicit model
constructors are the preferred Python construction interface. Implementation and
contract tests are still pending.

### 5. Structurally incomplete models versus writer failures

**Observed:** `TranslationUnit()` and `Ude(name="example")` are accepted despite
DTD `tuv+` and `map+` requirements. `TranslationUnit.items` also permits notes after
variants, which the DTD rejects. This follows the plan's “DTD owns order and
cardinality” direction, but conflicts with its claim that a writer DTD failure
necessarily means an internal model/projection bug rather than bad caller data.
An empty variant content tuple is different: it can represent a legal empty
`<seg/>`, because the XML builder will supply the wrapper.

**Questions:** may models represent incomplete construction states? If yes, what
error does writing a structurally invalid model raise, and does it permanently
fail the writer? If not, where are these structural constraints enforced without
creating a second schema implementation?

**Decision:** On being able to create an object like `TranslationUnit()` that
represents a incorrect state according to the DTD, we should error on creation.
On specifically the `TranslationUnit.items`, I would go the way of intentionally
separating the "main" content (so tuv for a tu, the seg content for a tuv), from
the metadata elements. Each are a tuple, to presever order, however on write,
we always ensure that we write the metadata elements first, in order, and then
the content elements, satisfying the DTD, and ensuring proper round-tripping
(technically order doesn't matter but if we can keep it, might as well).

### 6. Cross-field and segment-wide spec requirements

**Observed:** the spec's `Ude.base` requirement when a map carries `code` is not
implemented; the model docstring explicitly defers it. The spec also requires
paired `bpt`/`ept` codes within a segment and unique `bpt.i` values within that
segment (see the `bpt`, `ept`, and `i` sections). These are not DTD constraints and
there are currently no corresponding model validators.

**Proposed direction:** audit mandatory prose rules separately from recommendations
before claiming complete strictness. Decide validation scope for inline pairing,
including nested `hi`/`sub` content; the spec explicitly allows overlapping native
code pairs, so ordinary XML-style stack nesting would be the wrong rule.

**Decision:** Agreed with the proposed direction, we'll need to do a full audit of
the spec to catch any prose rule and add validators/warnings wherever needed.

### 7. Assignment safety for constraints involving several nodes

**Observed:** tuple fields prevent unchecked list mutation, but their child models
remain mutable. Adding `code` to an existing child `Map`, for example, would not
trigger validation of its parent `Ude`. `validate_assignment` on each model alone
cannot guarantee that an already-built tree still satisfies parent-level rules.

**Questions:** is assignment validation a local guarantee only, with complete
validation before serialization? Or should the model API prevent changes that
invalidate parents? Avoid promising that tuples solve cross-node mutation safety.

**Decision:** Trying to ensure parents are valid when assigning an attribute to the
child would enforce too much complexity, we document and accept that we can only
ensure that a given model is valid at assignment time, but that wider tree validaty
is only ensure either via a deliberate, user initiated `model_validate` or during
serialization in the writer.

### 8. Deprecated language attributes

**Observed:** `Note.lang` and `Property.lang` use `TMXLanguageTag`, whereas
`TranslationUnitVariant.lang` is plain `str`. The DTD still requires `xml:lang` on
`tuv`; legacy `lang` is permitted in addition, not as a DTD substitute for it.

**Proposed direction:** apply the language value contract consistently unless the
spec gives a reason not to. Explicitly settle whether simultaneously supplied
`lang` and `xml_lang` may differ; do not introduce equality or fallback behavior
without a spec/policy basis.

**Decision:** We should error on creation if only lang is provided. If only
xml:lang is provided, lang stays as None and just never gets serialized. If
they differ (either at assignment or on serialization) we warn, as this
*technically* is valid, but user should be made aware tools may reject or
only consider xml:lang

## XML boundary (defer until projection / I/O exists)

### 9. Semantic normalization and XML-representable text

**Observed:** `Note.text` and `Property.text` accept both `None` and `""`. Mixed
content tuples may contain adjacent strings and empty strings. XML does not
necessarily preserve those distinctions. Plain Python strings can also contain
characters that XML 1.0 cannot represent, independently of the valid Unicode scalar
range used for the textual `map unicode="#x..."` attribute.

**Questions:** normalize text at model construction or define round-trip equality
semantically? At which boundary are XML-illegal text characters rejected, with what
error? Tests must preserve significant whitespace while allowing only intentional
normalizations. Do not equate a textual code-point attribute with literal XML text.

**Decision:**

### 10. Input DOCTYPE and entity wording needs an executable contract

**Observed:** the plan says internal subsets are never loaded. Disabling external
DTD loading does not mean libxml2 ignores all internal-subset declarations. Parser
flags are implementation choices, not themselves proof of the security guarantee.

**Proposed direction:** settle the desired externally observable policy (for example,
DOCTYPE accepted but never authoritative, versus rejecting internal declarations).
Then verify no external-resource access, no untrusted defaults changing the modeled
data, and the chosen entity behavior using hostile fixtures. Do not weaken parsing
limits merely to make a fixture pass.

**Decision:**

## Housekeeping / verification later

- The plan and the `models.py` module docstring still refer to `types.py`, now
  `validators.py`; the code also has a separate `bcp47.py` module.
- `PLAN.md` says 100-character lines; `ruff.toml` configures 120. Follow the existing
  formatter until a preference is chosen.
- XML modules and `io.py` are placeholders; the error hierarchy only has
  `TmxWarning`. These are unfinished work, not failing-test targets yet.
- Verify the DTD is included in a built wheel and loadable through package resources
  outside the checkout. Its presence under `src/` is not proof of wheel inclusion.
- No coverage/property-testing dependency or CI configuration has been added.
  Explicit examples are the first slice; choose additional tooling when useful.
