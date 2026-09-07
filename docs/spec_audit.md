# TMX 1.4b — DTD-Expressibility Audit (independent subagent output)

## Sanity pass: what the DTD already expresses (do not count these as gaps)

- **Structure/occurrence**: `tmx(header, body)`, `header (note|prop|ude)*`, `body (tu*)`, `tu ((note|prop)*, tuv+)`, `tuv ((note|prop)*, seg)`, `ude (map+)`, `map EMPTY` — element order, optionality, and "one or more" cardinalities (≥1 `tuv`, exactly 1 `seg`, ≥1 `map`) are all in the content models.
- **Required attributes**: all `#REQUIRED` declarations match the spec's "Required attributes" lists exactly (`header`: 7 attrs; `tuv`/`xml:lang`; `ude`/`name`; `map`/`unicode`; `bpt`/`i`; `ept`/`i`; `it`/`pos`).
- **Enumerations**: `segtype` via `%segtypes;` = `(block|paragraph|sentence|phrase)` on `header` and `tu`, and `it`/`pos` = `(begin|end)` — these DTD-enumerated value spaces are already enforced; don't re-list them as gaps.
- **version**: `<!ATTLIST tmx version CDATA #FIXED "1.4">` — the #FIXED default enforces "if present, must be 1.4" and supplies "1.4" when absent (see contradictions: the spec calls it *required*, #FIXED in XML does not require presence).
- **Lowercase names**: "All elements and attributes names of TMX are defined in **lowercase**" is enforced implicitly by the literal names in the DTD — no gap.
- **Five entities**: the DTD declares exactly `amp gt lt quot apos`, matching §1.2's "only the following five character entity references are allowed" (other entities would be undeclared and thus a well-formedness error in XML anyway).
- **The `base`-if-`code` rule is *acknowledged* in the DTD only as a comment** (`<!-- Note: the base attribute is required if... -->`). A comment enforces nothing — it remains a genuine gap (M7 below), but note the DTD authors knew about it.
- The DTD carries deprecated `lang` on `note`, `prop`, `tuv` with a "use xml:lang" comment — a deliberate backward-compat superset of the spec's attribute tables, not a contradiction.

---

## Mandatory rules the DTD cannot express

1. **bpt/ept pairing with ordering**
   - Quote: "They can be in any order, except that each `<bpt>` element must have a subsequent corresponding `<ept>` element." (§3.1.1 `<seg>`; repeated verbatim under `<hi>` and `<sub>` Contents)
   - Constrains: `seg`, `hi`, `sub` content.
   - Scope: cross-element within one segment.
   - Strength: MANDATORY ("must").
   - Why DTD fails: the content model `(#PCDATA|bpt|ept|ph|it|hi|ut)*` is a flat, unordered repetition; a DTD regex can express neither pairing nor the "subsequent" ordering/nesting relation between two repeated alternatives.

2. **i uniqueness among bpt within a seg**
   - Quote: "Number. Must be unique for each `<bpt>` within a given `<seg>` element." (§3.2.1 `i`)
   - Constrains: `bpt`/`i`.
   - Scope: cross-element within one segment (uniqueness scope).
   - Strength: MANDATORY ("Must").
   - Why DTD fails: DTD has no scoped-uniqueness mechanism. `ID` would enforce *document-wide* uniqueness and requires the Name production (values like "1" are illegal), and the required scope is per-`seg`, not per-document.

3. **i values must be numbers**
   - Quote: "Value description: Number." (§3.2.1 `i`)
   - Constrains: `bpt`/`i`, `ept`/`i`.
   - Scope: single element value.
   - Strength: MANDATORY (normative value description).
   - Why DTD fails: declared as `CDATA`; DTD would need `NUMBER` (an SGML construct XML DTDs don't support for XML validation).

4. **ept matched to bpt via identical i**
   - Quote: "The attribute `i` is used to pair the `<bpt>` elements with `<ept>` elements." and "The attribute `i` is used to specify which `<ept>` is closing which `<bpt>`" (§3.2.1 `i`); reinforced by "Note that an `<ept>` element is matched based on x attribute of its corresponding `<bpt>` element." (§3.2.1 `x`)
   - Constrains: `bpt`/`i` ↔ `ept`/`i`.
   - Scope: cross-element within a segment.
   - Strength: MANDATORY (definitional pairing mechanism).
   - Why DTD fails: no key/foreign-key mechanism; `IDREF` would require document-wide IDs and can't express "the ept's i must equal a *bpt's* i in the same seg."

5. **x values must be numbers**
   - Quote: "Value description: Number." (§3.2.1 `x`)
   - Constrains: `bpt`, `it`, `ph`, `hi` / `x`.
   - Scope: single element value.
   - Strength: MANDATORY (normative value description).
   - Why DTD fails: `CDATA` declared value; no numeric declared value exists in XML DTDs.

6. **x matches inline elements across tuvs of one tu**
   - Quote: "The x attribute is used to match inline elements `<bpt>`, `<it>`, `<ph>`, and `<hi>` between each `<tuv>` element of a given `<tu>` element." (§3.2.1 `x`; again in §4.3: "each element with a given attribute `x` ... has a matching element in the target segment")
   - Constrains: `x` on `bpt`/`it`/`ph`/`hi`, transitively `ept` (via its bpt).
   - Scope: cross-element across sibling `tuv`s of one `tu`.
   - Strength: MANDATORY (the mechanism Level 2 compliance is verified against).
   - Why DTD fails: no constraint links attribute values of elements in *sibling subtrees*; DTDs are strictly context-free per element.

7. **ude/base required iff any map child has code**
   - Quote: "If the `code` attribute is specified, the parent `<ude>` element must specify a `base` attribute." (§3.1.1 `<map/>` Optional attributes; repeated in `<ude>`: "`base` (required if one or more of the `<map/>` elements contains a `code` attribute)"; also a DTD *comment*)
   - Constrains: `ude`/`base` ↔ `map`/`code`.
   - Scope: cross-field between parent attribute and child attribute.
   - Strength: MANDATORY ("must").
   - Why DTD fails: DTDs cannot condition one element's attribute presence on another element's attribute; conditional requirements between parent/child are inexpressible.

8. **code format: hex with "#x" prefix**
   - Quote: "Hexadecimal value prefixed with "#x". For example: code="#x9F"." (§3.2.1 `code`)
   - Constrains: `map`/`code`.
   - Scope: single element value.
   - Strength: MANDATORY (normative value description).
   - Why DTD fails: `CDATA` admits any string; DTDs have no pattern/regex facet for attribute values (an enumeration is impossible for an open-ended set of hex values).

9. **unicode: valid Unicode code point in hex**
   - Quote: "A valid Unicode value (including values in the Private Use areas) in hexadecimal format. For example: unicode="#xF8FF"." (§3.2.1 `unicode`; preceded by the truncated sentence "Its value must be a" — see ambiguities)
   - Constrains: `map`/`unicode`.
   - Scope: single element value.
   - Strength: MANDATORY ("must be a [valid Unicode value...]" per the truncated lead-in).
   - Why DTD fails: no value-pattern mechanism; "valid Unicode code point" is a semantic predicate far beyond any DTD declared value.

10. **ent must be ASCII**
    - Quote: "Text in ASCII. For example: ent="copy"." (§3.2.1 `ent`)
    - Constrains: `map`/`ent`.
    - Scope: single element value.
    - Strength: MANDATORY (normative value description).
    - Why DTD fails: `CDATA` is character data with no charset restriction on the *content* of the value; DTDs cannot restrict which code points appear in an attribute.

11. **subst must be ASCII**
    - Quote: "A text in ASCII. For example: subst="(c)" for the copyright sign." (§3.2.1 `subst`)
    - Constrains: `map`/`subst`.
    - Scope: single element value.
    - Strength: MANDATORY (normative value description).
    - Why DTD fails: same as above — no character-range constraint mechanism.

12. **tuid: no whitespace**
    - Quote: "Text without white spaces." (§3.2.1 `tuid`)
    - Constrains: `tu`/`tuid`.
    - Scope: single element value.
    - Strength: MANDATORY (normative value description).
    - Why DTD fails: the DTD explicitly abandoned `NMTOKEN` for `CDATA` (per the DTD's own change history: "replaced NMTOKEN by CDATA for all NAME attributes"); `NMTOKEN` would have partially enforced this, `CDATA` does not.

13. **usagecount must be a number**
    - Quote: "Value description: Number." (§3.2.1 `usagecount`)
    - Constrains: `tu`/`usagecount`, `tuv`/`usagecount`.
    - Scope: single element value.
    - Strength: MANDATORY (normative value description).
    - Why DTD fails: `CDATA`; no numeric declared value in XML DTDs.

14. **Date attributes in ISO 8601**
    - Quote: "Date in [ISO 8601] Format. The recommended pattern to use is: YYYYMMDDThhmmssZ" (§3.2.1 `creationdate`, `changedate`, `lastusagedate` — identical text in each)
    - Constrains: `header`, `tu`, `tuv` / `creationdate`, `changedate`, `lastusagedate`.
    - Scope: single element value.
    - Strength: MANDATORY for ISO 8601 conformance (normative value description); the specific `YYYYMMDDThhmmssZ` pattern is only RECOMMENDED (split off as R5).
    - Why DTD fails: `CDATA` with no pattern mechanism; date/time well-formedness is a lexical+semantic constraint DTDs cannot state.

15. **Language codes per RFC 3066**
    - Quote: "A language code as described in the [RFC 3066]." (§3.2.1 `adminlang`, `srclang`; §3.2.2 `xml:lang`)
    - Constrains: `header`/`adminlang`, `header`+`tu`/`srclang`, `tuv`/`xml:lang`, `note`/`xml:lang`, `prop`/`xml:lang`.
    - Scope: single element value.
    - Strength: MANDATORY (normative value description citing a normative reference).
    - Why DTD fails: `CDATA`; language-tag well-formedness is a grammar over the value, not expressible in any DTD declared value.

16. **Case-insensitivity of adminlang, srclang, xml:lang values**
    - Quote: "Unlike the other TMX attributes, the values for adminlang are not case-sensitive." (§3.2.1 `adminlang`; parallel sentences under `srclang` and `xml:lang`)
    - Constrains: values of `adminlang`, `srclang`, `xml:lang` (e.g., sample doc mixes `srclang="EN"` with `adminlang="en-us"`).
    - Scope: single element value (comparison semantics), with cross-element effect via M18.
    - Strength: MANDATORY (normative semantic; the sample relies on it).
    - Why DTD fails: DTD attribute matching is exact-string; DTDs have no case-normalization or case-insensitive-comparison mechanism (nothing like SGML's name-case generalization applies to CDATA values).

17. **Attribute inheritance: segtype falls back to header**
    - Quote: "If a `<tu>` element does not have a segtype attribute specified, it uses the one defined in the `<header>` element." (§3.2.1 `segtype`)
    - Constrains: `tu`/`segtype` ← `header`/`segtype`.
    - Scope: document-level (cross-element defaulting).
    - Strength: MANDATORY (defining semantics of the attribute).
    - Why DTD fails: DTD `#IMPLIED` yields no value; a DTD default would be a fixed literal, not a runtime reference to another element's attribute value.

18. **Attribute inheritance: srclang falls back to header; tuv/xml:lang must equal srclang (unless "*all*")**
    - Quote: "the `<tuv>` holding the source segment will have its `xml:lang` attribute set to the same value as srclang. (except if srclang is set to "*all*"). If a `<tu>` element does not have a srclang attribute specified, it uses the one defined in the `<header>` element." (§3.2.1 `srclang`)
    - Constrains: `header`/`srclang`, `tu`/`srclang`, `tuv`/`xml:lang`; special value `*all*`.
    - Scope: document-level / cross-element within a tu.
    - Strength: MANDATORY (see ambiguities — the correspondence clause is declarative prose, but it defines the attribute's meaning).
    - Why DTD fails: two inexpressible things at once — attribute-value inheritance across elements, and an equality constraint between an element's attribute and a header attribute, plus a magic value that would break any enumeration.

19. **adminlang is the default language for note/prop**
    - Quote: "Specifies the default language for the administrative and informative elements `<note>` and `<prop>`." (§3.2.1 `adminlang`)
    - Constrains: `header`/`adminlang` → `note`, `prop` lacking `xml:lang`.
    - Scope: document-level defaulting.
    - Strength: MANDATORY (defining semantics).
    - Why DTD fails: DTD cannot make one element's attribute supply a default for other elements' attributes.

20. **datatype defaults to "unknown"**
    - Quote: ""unknown" = undefined (default)" and "Default value: "unknown"." (§3.2.1 `datatype`)
    - Constrains: `datatype` on `header` (required there), `tu`, `tuv`, `sub`.
    - Scope: single-element default value semantics.
    - Strength: MANDATORY (stated as "Default value").
    - Why DTD fails: `#IMPLIED` supplies no value; a DTD literal default ("unknown" instead of #IMPLIED) would change the semantics — the attribute would appear *present* to applications, which the spec does not say.

21. **assoc value space: p / f / b**
    - Quote: ""p" (the element is associated with the text preceding the element), "f" (the element is associated with the text following the element), or "b" (the element is associated with the text on both sides)." (§3.2.1 `assoc`)
    - Constrains: `ph`/`assoc`.
    - Scope: single element value.
    - Strength: MANDATORY (closed value description; unlike datatype/type no "not exhaustive" hedge).
    - Why DTD fails: **this one the DTD could have expressed** — an enumerated declared value, exactly as done for `pos` and `segtype` — but declares `assoc CDATA #IMPLIED`. Listed as a gap because the DTD mechanism exists and was not used.

22. **seg content: no leading/trailing whitespace**
    - Quote: "Text data (without leading or trailing white spaces characters)," (§3.1.1 `<seg>` Contents)
    - Constrains: `seg` (and by the same Contents wording, `hi` and `sub`).
    - Scope: single element value (mixed content).
    - Strength: MANDATORY (listed under normative Contents; parenthetical restriction).
    - Why DTD fails: `#PCDATA` in a mixed content model cannot be constrained; DTDs have no whitespace-normalization or text-pattern rules for element content.

23. **`<ut>` is deprecated and forbidden in Level 2 documents**
    - Quote: "**This element has been DEPRECATED.**" (§3.1.2 `<ut>`); "The use of `<ut>` is not allowed in compliant documents." (§4.3)
    - Constrains: `ut`.
    - Scope: document-level (Level 2 conformance).
    - Strength: MANDATORY for Level 2 compliance ("not allowed"); deprecation itself has no defined sanction for Level 1.
    - Why DTD fails: DTDs have no notion of deprecation; the element is a first-class citizen of every content model (`seg`, `sub`, `hi`, `ut` itself). No DTD mechanism can forbid it conditionally on a conformance level.

24. **Level 2 parity and stripping assumptions**
    - Quote: "The translated segments does not have more or less tags than the source segments. (No additional tags was added, or removed)." and "The tags `<hi>` and `<sub>` are stripped out of all segments." (§4.3, "Assuming:") — plus the verification rule that matching segments have "the same number of inline elements, in the same order and of the same kind".
    - Constrains: inline elements across all `tuv`s of a `tu` (Level 2 documents).
    - Scope: cross-element across sibling segments.
    - Strength: MANDATORY within the Level 2 definition (these are the stated preconditions of compliance).
    - Why DTD fails: count/order/kind equality between the inline elements of sibling subtrees is entirely outside DTD expressive power (no cross-tree constraints, no counting).

25. **Encoding constraints on the file, not the markup**
    - Quote: "They can use either of three encoding methods: UTF-16 (16-bit files), UTF-8 (8-bit files) or ISO-646 [a.k.a. US-ASCII] (7-bit files)." ; "For 7-bit files, extended (non-ASCII) characters are always represented by numeric character references." ; "Note that UTF-16 files always start with the Unicode byte-order-mark (BOM) value: U+FEFF." (§1.2)
    - Constrains: the physical document.
    - Scope: document-level.
    - Strength: MANDATORY ("can use either of three", "always").
    - Why DTD fails: DTDs describe the prologue-independent logical structure; entity declarations say nothing about the document's byte encoding, BOM, or character-reference usage.

---

## Recommendations and conventions (not requirements)

1. **map: at least one of code/ent/subst**
   - Quote: "At least one of these attributes should be specified." (§3.1.1 `<map/>`)
   - Constrains: `map`/`code`, `ent`, `subst`. Scope: cross-field within one element. Strength: RECOMMENDED ("should" — though the adjacent `base` clause in the same sentence is "must", listed as M7).
   - Why DTD can't express it: even a "should" over an any-of-three-attributes disjunction is beyond DTD conditional logic.

2. **x- prefix for unpublished prop types**
   - Quote: "If the tool exports unpublished properties types, their values should begin with the prefix "x-"." (§3.1.1 `<prop>`)
   - Constrains: `prop`/`type` values. Scope: single element value. Strength: RECOMMENDED.
   - Why DTD can't: value-pattern/prefix constraint on CDATA; also conditional on publish-status, an extra-DTD fact.

3. **Recommended datatype values**
   - Quote: "The recommended values for the datatype attribute are as follow (this list is not exhaustive)" (§3.2.1 `datatype`, ~25 listed values)
   - Constrains: `datatype` values. Scope: single element value. Strength: RECOMMENDED (explicitly non-exhaustive).
   - Why DTD can't: even the *mandatory* part is open-ended "Text"; an enumeration would wrongly close the value space.

4. **Recommended `type` values**
   - Quote: "The recommended values for the type attribute, when used in `<bpt>` and `<it>` are as follow (this list is not exhaustive)" (§3.2.1 `type`; second list for `<ph>`)
   - Constrains: `type` on `prop`, `bpt`, `ph`, `hi`, `sub`, `it`. Scope: single element value. Strength: RECOMMENDED (non-exhaustive; note also the spec's own header list "index/date/time/..." is presented without a "recommended" hedge — mild internal inconsistency).
   - Why DTD can't: open-ended value space, element-dependent, non-exhaustive.

5. **Recommended date pattern**
   - Quote: "The recommended pattern to use is: YYYYMMDDThhmmssZ" (§3.2.1 `changedate`, `creationdate`, `lastusagedate`)
   - Constrains: date attribute lexical form. Scope: single element value. Strength: RECOMMENDED (the ISO 8601 requirement itself is counted as M14).
   - Why DTD can't: no pattern mechanism.

6. **Prefer sentence-level segmentation**
   - Quote: "it is recommended that you use such segmentation rather than a specific, proprietary method like the one above." (§3.2.1 `segtype`)
   - Constrains: authoring practice, no element/attribute value per se. Scope: document-level. Strength: RECOMMENDED.
   - Why DTD can't: authoring guidance, not a document constraint.

7. **IANA charset identifiers "if possible"**
   - Quote: "One of the [IANA] recommended "charset identifier", if possible." (§3.2.1 `o-encoding`; same for `base`)
   - Constrains: `o-encoding`, `ude`/`base` values. Scope: single element value. Strength: RECOMMENDED ("if possible" softens it; a non-IANA string is not clearly a violation).
   - Why DTD can't: open enumeration external to the document.

8. **Publish tool identifiers / property types / ude names**
   - Quote: "each tool provider should publish the string identifier it uses." (§3.2.1 `creationtool`, `creationtoolversion`); "It is the responsibility of each tool provider to publish the types and values of the properties it uses." (§3.1.1 `<prop>`); "tools providers should publish the values they use." (§3.2.1 `name`)
   - Constrains: out-of-band documentation, not document content. Scope: document-level/external. Strength: RECOMMENDED.
   - Why DTD can't: not a document constraint at all.

9. **"Logically" two or more tuvs**
   - Quote: "Logically, a complete translation-memory database will contain at least two `<tuv>` elements in each translation unit." (§3.1.1 `<tu>`)
   - Constrains: `tu` cardinality. Scope: single element. Strength: CONVENTION/EXAMPLE ("logically", "will" describes typical databases; DTD correctly requires only 1+).
   - Why DTD can't: DTD already expresses the actual floor (`tuv+`); the "at least two" is descriptive.

10. **Grouping and ordering conventions (§5.1)**
    - Quote: "you can specify a `<prop>` element for each of the `<tu>` which comprise the group." ; "If the order of the `<tu>` elements is relevant, you may want to use the `tuid` attribute or a `<prop>` element to reflect it."
    - Constrains: conventions using `prop`/`type="group"` and `tuid`. Scope: document-level. Strength: CONVENTION/EXAMPLE ("can", "may want").
    - Why DTD can't: pure convention on how optional facilities may be used.

11. **Validate suspicious files**
    - Quote: "any suspicious TMX file should be verified against the TMX DTD using a validating XML parser." (§1.1)
    - Constrains: consumer behavior. Scope: document-level/process. Strength: RECOMMENDED.
    - Why DTD can't: process advice.

12. **Namespace usage example**
    - Quote: "The TMX namespace is defined as "<http://www.lisa.org/tmx14>"." with example using `xmlns="http://www.lisa.org/tmx14"` (§1.1)
    - Constrains: namespace URI when embedding TMX. Scope: document-level. Strength: CONVENTION/EXAMPLE (stated but only illustrated; note the DTD has no namespace machinery at all, and the example's `version="1.4"` aligns with #FIXED).
    - Why DTD can't: DTDs predate XML namespaces; no mechanism to constrain xmlns attributes' values or scope.

13. **Sample-document notational conventions and content**
    - Quote: "**BOLD** for the items that are mandatory..." (Appendix A preamble) and the sample document itself (e.g., `datatype="PlainText"`, `datatype="Text"`, `srclang="EN"`)
    - Constrains: nothing normative — it is an illustration. Scope: document-level. Strength: CONVENTION/EXAMPLE. (Note the sample's `PlainText`/`Text` capitalizations contradict the lowercase recommended datatype values in §3.2.1 — legal, since values are untyped, but a bad precedent to copy.)
    - Why DTD can't: informative by declaration.

---

## Ambiguities and contradictions

**Ambiguities:**

- **Truncated sentence in `unicode`**: "Its value must be a" (§3.2.1 `unicode`) — the sentence is cut off mid-thought before "Value description:". Two readings: (a) it's merely a typo'd lead-in duplicating the value description that follows; (b) it originally completed a stronger "must be a valid Unicode code point" constraint. I treated it as mandatory either way, but the exact strength rests on a broken sentence.
- **`assoc` strength**: the value description reads as a closed enumeration ("p", "f", or "b"), but unlike `pos` it is not echoed in the element section as an enumerated attribute; a lenient reader could treat the parentheticals as explanation rather than restriction. I classified it MANDATORY (no "recommended"/"not exhaustive" hedge, unlike datatype/type).
- **`srclang` ↔ `xml:lang` correspondence**: "the `<tuv>` holding the source segment will have its `xml:lang` attribute set to the same value as srclang" — "will" can be read as a normative guarantee required of documents, or as a description of how well-behaved producers behave (in which case a consumer cannot reject a file over it). I listed it MANDATORY; a validator-design reader could reasonably demote it.
- **`x` required vs optional**: §C says "Made the attribute `x` required instead of optional" (1.4 changes), then 1.4a says "Reversed the attribute `x` to optional," and §C lists the 1.4b correction "Corrected the `<bpt>` definition that listed the `x` attribute in as required attribute." The narrative is internally confusing, but DTD (`x CDATA #IMPLIED`) plus the element sections (x always listed under Optional) settle it for 1.4b: **x is optional**.
- **`version` presence**: §3.1.1 `<tmx>` lists `version` under "Required attributes", but the DTD's `#FIXED "1.4"` in XML does not require presence (a conforming parser supplies the default when absent). Strictly, a document with no `version` attribute is DTD-valid but violates the spec's "required" list — a genuine, if small, DTD/spec mismatch in *both* directions at once.
- **Level 2 "assumptions"**: §4.3 frames tag-parity and hi/sub-stripping under "Assuming:" — it is unclear whether these are conditions a *document* must satisfy to be Level 2 compliant, or preconditions of the compliance *test procedure*. I listed them as MANDATORY within the Level 2 definition; they are not constraints on Level 1 documents at all.

**Genuine DTD/spec contradictions:**

1. **Spec URL points at the wrong DTD**: Appendix B says "The document type definition file for TMX is available at: [http://www.lisa.org/tmx/tmx15.dtd]" — the filename says *tmx15* while the document and DTD header are version 1.4. Almost certainly a spec typo, but as written the prose contradicts the DTD's own `#FIXED "1.4"`.
2. **Deprecated `lang` attribute**: the DTD declares `lang CDATA #IMPLIED` with a "deprecated: use xml:lang" comment on `note`, `prop`, and `tuv`; the spec's element sections (§3.1.1 `<note>`, `<prop>`, `<tuv>`) and §3.2.2 do not document `lang` at all. Not a logical conflict (the DTD is a deliberate backward-compatibility superset, per its own change log "put back lang in the DTD for backward compatibility"), but a validator written from the prose alone would reject attributes the DTD accepts.
3. **`assoc`**: spec value description defines exactly three values; DTD says `CDATA`. Not a logical contradiction (CDATA doesn't *permit* p/f/b specifically), but it is a constraint the DTD's own mechanism (enumeration, used for `pos` and `segtype`) could have captured and didn't — the single clearest case of the DTD under-specifying where its own tools sufficed.
