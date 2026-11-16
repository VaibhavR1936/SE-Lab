import pytest
from password_policy import check_password, strength, suggest_fix


# -------------------------------
# CHECK_PASSWORD TEST CASES
# -------------------------------

def test_valid_password():
    assert check_password("Abcdef1!") == []


def test_password_too_short():
    assert "too short" in check_password("Ab1!")


def test_password_too_long():
    assert "too long" in check_password("A" * 65)


def test_common_password():
    assert "common" in check_password("password")


def test_missing_uppercase():
    assert "no uppercase" in check_password("abcdef1!")


def test_missing_lowercase():
    assert "no lowercase" in check_password("ABCDEF1!")


def test_missing_digit():
    assert "no digit" in check_password("Abcdefgh!")


def test_missing_special_character():
    assert "no special" in check_password("Abcdef12")


def test_empty_password():
    issues = check_password("")
    assert "too short" in issues


# -------------------------------
# STRENGTH TEST CASES
# -------------------------------

def test_strong_password():
    assert strength("Abcdefghijkl1!") == "strong"


def test_good_password():
    assert strength("Abcdef1!") == "good"


def test_weak_password():
    assert strength("Abcdefgh1") == "weak"


def test_very_weak_password():
    assert strength("") == "very weak"


# -------------------------------
# SUGGEST_FIX TEST CASES
# -------------------------------

def test_no_fix_needed():
    assert suggest_fix([]) == "none needed"


def test_fix_too_short():
    assert suggest_fix(["too short"]) == "add more characters"


def test_fix_common_password():
    assert suggest_fix(["common"]) == "avoid common passwords"


def test_fix_missing_character_type():
    assert suggest_fix(["no uppercase"]) == "add uppercase"


def test_fix_too_long():
    assert suggest_fix(["too long"]) == "shorten it"