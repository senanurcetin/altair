"""
Independent QA for filter scoping in Altair PR #4189.

The QA suite is intentionally separate from the contribution branch.
The reference semantics are alt.layer(filtered, new_layer).
"""

import pandas as pd
import pytest

import altair as alt


@pytest.mark.parametrize("operator", ["add", "iadd", "add_layers"])
@pytest.mark.parametrize("new_layer_has_data", [False, True])
def test_dataless_filtered_layer_does_not_filter_added_layer(
    operator, new_layer_has_data
):
    # No data in the original layers: data ownership is not hoisted.
    bars = alt.Chart().mark_bar().encode(x="x:O", y="y:Q")
    ticks = alt.Chart().mark_tick().encode(x="x:O", y="y:Q")
    original = (bars + ticks).transform_filter("datum.y > 10")
    assert "data" not in original.to_dict()

    other = (
        alt.Chart(pd.DataFrame({"x": [1, 2], "y": [1, 2]}))
        .mark_point()
        .encode(x="x:O", y="y:Q")
        if new_layer_has_data
        else alt.Chart().mark_rule().encode(y=alt.datum(5))
    )
    expected = alt.layer(original, other).to_dict()
    if operator == "add":
        actual = (original + other).to_dict()
    elif operator == "iadd":
        current = original.copy(deep=True)
        current += other
        actual = current.to_dict()
    else:
        actual = original.add_layers(other).to_dict()

    # A filter on the old chart must not be hoisted to the new chart.
    assert actual == expected
    assert "transform" not in actual
    assert actual["layer"][0]["transform"] == [{"filter": "datum.y > 10"}]
    assert "transform" not in actual["layer"][1]
