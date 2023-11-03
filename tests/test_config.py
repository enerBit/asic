import asic.config


def test_with_exact_quantifiers_pattern_to_template():
    patt = "(?P<location_month>[0-9]{2})"
    expect = "{location_month:2}"
    result = asic.config.pattern_to_template(patt)
    assert result == expect


def test_with_no_quantifiers_pattern_to_template():
    patt = "(?P<ext_excel>xlsx)"
    expect = "{ext_excel}"
    result = asic.config.pattern_to_template(patt)
    assert result == expect


def test_with_combined_patterns_pattern_to_template():
    patt = "(?P<code>[a-zA-Z0-9-_]*)(?P<name_year>[0-9]{4}).*(?P<name_month>[0-9]{2}).*(?P<name_day>[0-9]{2}).(?P<ext_excel>xlsx)"
    expect = "{code}{name_year:4}.*{name_month:2}.*{name_day:2}.{ext_excel}"
    result = asic.config.pattern_to_template(patt)
    assert result == expect
