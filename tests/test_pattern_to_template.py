from asic.files.file import pattern_to_template


def test_with_exact_quantifiers_pattern_to_template():
    patt = "(?P<location_month>[0-9]{2})"
    expect = "{location_month:02}"
    result = pattern_to_template(patt)
    assert result == expect


def test_with_no_quantifiers_pattern_to_template():
    patt = "(?P<ext_excel>xlsx)"
    expect = "{extension}"
    result = pattern_to_template(patt)
    assert result == expect


def test_with_ext_excel_pattern_to_template():
    patt = "(?P<ext_excel>xlsx)"
    expect = "{extension}"
    result = pattern_to_template(patt)
    assert result == expect


def test_with_ext_versioned_pattern_to_template():
    patt = "(?P<ext_versioned>xlsx)"
    expect = "{extension}"
    result = pattern_to_template(patt)
    assert result == expect


def test_with_combined_patterns_pattern_to_template():
    patt = "(?P<name_agent>[a-zA-Z]{4})_(?P<code>fronterascomerciales)_(?P<name_day>[0-9]{2})-(?P<name_month>[0-9]{2})-(?P<name_year>[0-9]{4}).(?P<ext_excel>xlsx)"
    expect = "{name_agent}_fronterascomerciales_{name_day:02}-{name_month:02}-{name_year:04}.{extension}"
    result = pattern_to_template(patt)
    assert result == expect
