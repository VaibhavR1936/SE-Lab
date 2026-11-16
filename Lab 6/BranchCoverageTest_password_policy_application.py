import pytest
from password_policy import check_password, strength, suggest_fix


# =====================================
# CHECK_PASSWORD – BRANCH TESTING
# =====================================

def test_length_less_than_8():
    assert "too short" in check_password("Ab1!")


def test_length_between_8_and_64():
    assert check_password("Abcdef1!") == []


def test_length_greater_than_64():
    assert "too long" in check_password("A" * 65)


def test_common_password_branch_true():
    assert "common" in check_password("password")


def test_common_password_branch_false():
    assert "common" not in check_password("Abcdef1!")


def test_uppercase_branch():
    assert "no uppercase" in check_password("abcdef1!")


def test_lowercase_branch():
    assert "no lowercase" in check_password("ABCDEF1!")


def test_digit_branch():
    assert "no digit" in check_password("Abcdefgh!")


def test_special_character_branch():
    assert "no special" in check_password("Abcdef12")


def test_all_character_types_present():
    assert check_password("Abcdef1!") == []


# =====================================
# STRENGTH – BRANCH TESTING
# =====================================

def test_no_issues_branch():
    assert strength("Abcdef1!") == "good"


def test_password_length_at_least_14():
    assert strength("Abcdefghijkl1!") == "strong"


def test_password_length_below_14():
    assert strength("Abcdef1!") == "good"


def test_issues_less_than_or_equal_to_2():
    assert strength("Abcdefgh1") == "weak"


def test_issues_greater_than_2():
    assert strength("") == "very weak"


# =====================================
# SUGGEST_FIX – BRANCH TESTING
# =====================================

def test_empty_issues_branch():
    assert suggest_fix([]) == "none needed"


def test_too_short_branch():
    assert suggest_fix(["too short"]) == "add more characters"


def test_common_password_branch():
    assert suggest_fix(["common"]) == "avoid common passwords"


def test_missing_character_branch():
    assert suggest_fix(["no digit"]) == "add digit"


def test_default_suggestion_branch():
    assert suggest_fix(["too long"]) == "shorten it"