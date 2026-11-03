"""Regression for informative enum-or-type validation errors (GH#3521)."""

import pytest

import altair as alt
from altair.utils.schemapi import SchemaValidationError


def test_invalid_string_sort_mentions_the_allowed_string_choices():
    chart = (
        alt.Chart({"values": [{"value": "a"}]})
        .mark_point()
        .encode(alt.X("value:N", sort="missing_column"))
    )
    with pytest.raises(SchemaValidationError) as caught:
        chart.to_dict()
    message = str(caught.value)
    assert "One of ['ascending', 'descending']" in message
    assert "Or a string matching one of the options above" in message
    assert "Mapping[str, Any]" in message


def test_named_sort_option_and_explicit_order_remain_valid():
    data = {"values": [{"value": "a"}, {"value": "b"}]}
    for sort in ("ascending", ["b", "a"]):
        chart = alt.Chart(data).mark_point().encode(alt.X("value:N", sort=sort))
        assert chart.to_dict()["encoding"]["x"]["sort"] == sort
