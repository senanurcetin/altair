# Altair #4189 — independent transform-scope QA, 2026-10-27

Upstream PR: https://github.com/vega/altair/pull/4189
Tested upstream PR head: `1c93a5bf3c96f09113b01a498059fcd1e035cdcb`
Old base tested: `ea8eb0cf209e0a40a5188107f8a0957ee4d090d8`
Fork QA branch: `qa/altair-4189-transform-scope-20261027`.

**Do not treat the QA branch as part of the live PR.** Neither the active contributor branch nor the upstream PR was modified; no additional upstream CI rerun or maintainer ping was requested.

## Precise finding

The PR aims to align chained `+`, `+=`, and `add_layers()` with explicit
`alt.layer()` data-ownership and transform-scoping semantics.

If the existing layered chart is **filtered and has no parent data**, the
`LayerChart.__iadd__` restore/nest branch is skipped because its entry
condition requires `self.data is not Undefined`. The resulting Vega-Lite
schema leaves the old filter at the newly combined parent level rather than
inside the original nested layer (unlike `alt.layer(filtered, added)`).

Six parametrized checks (three operators x new data-backed versus data-less
layer) fail against both unmodified PR head **and the old base**, so **this
is not a newly introduced #4189 regression**; it is an existing schema
consistency gap within the PR's stated scope.

The *QA-only candidate* adds an alternate entry condition:
`self.data is Undefined and self.transform is not Undefined`, using the
existing nested-layer branch. The test cases then match `alt.layer()`
and the old filter remains scoped to the original component.

This is a minimal, nine-line diff (six additions, three deletions) in
`altair/vegalite/v6/api.py`, not a proposal to silently change current
users' rendering behavior outside a major-release compatibility decision.

## A/B and test evidence

- Before QA-only fix, 6/6 new schema-consistency checks **fail** on both
  `ea8eb0c` and `1c93a5b` (expected negative controls).
- After QA-only fix, all 6 schema-consistency checks **pass**.
- Three additional real SVG render checks assert independently supplied
  two-point data remains visible. They **pass on both the old base and
  QA-only candidate**: these cases did **not** demonstrate a visible mark
  count regression. Do not claim a rendering bug from the schema mismatch.
- Python 3.11: `test_api.py`, `test_layer_props.py`,
  `test_layer_data_order.py`, and the original six QA cases:
  **264 passed, 10 skipped, 1 xfailed, 1 xpassed** (16 warnings).
- Python 3.13 with `vl_convert` installed, the same existing test files plus
  all nine QA cases: **277 passed, 2 skipped** (9 warnings), no failures.
  Existing SVG tests ran in this environment.

Reproduction (Windows QA clone at PR head, applying QA-only source diff):

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
py -3.13 -m pytest -q -o addopts= \
  tests/vegalite/v6/test_api.py \
  tests/vegalite/v6/test_layer_props.py \
  tests/vegalite/v6/test_layer_data_order.py \
  qa_evidence/test_dataless_filtered_parent_scope.py \
  --disable-warnings --tb=line
```

`ruff check` and `ruff format --check` passed for the QA Python test file.
`ruff check --ignore I001` passed for the production candidate, and
`git diff --check` passed. The default `I001` import-order warning was
confirmed to exist on the **unmodified base** at `api.py:57`. On Windows,
Ruff's full-file format check of `api.py` disagreed with CRLF line endings;
the source file was not wholesale reformatted.

## Notebook 1 handoff

The older maintainer discussion includes a **CHANGES_REQUESTED** review
and the possibility of postponing the wider semantic change until the next
Altair major release. CI success on the original PR head does not override
review or release-policy decisions. Evaluate whether the narrow QA fix
belongs in #4189, a follow-up, or the next major release; preserve the
reviewer's intended data-ownership semantics.

If taking the change forward, cherry-pick/adapt the API diff and the nine
QA tests, keeping them in an appropriate upstream test file rather than
blindly merging `qa_evidence/`. Additional real-world migration examples
and broader render compatibility remain out of this test's scope.
