import pytest
from src.domain.value_objects.sentiment_label import SentimentLabel
from src.domain.value_objects.cleaned_text import CleanedText


def test_sentiment_label_values():
    assert SentimentLabel.POSITIVO.value == "positivo"
    assert SentimentLabel.NEGATIVO.value == "negativo"
    assert SentimentLabel.NEUTRAL.value == "neutral"


def test_sentiment_label_from_string_valid():
    assert SentimentLabel.from_string("positivo") == SentimentLabel.POSITIVO
    assert SentimentLabel.from_string("POSITIVO") == SentimentLabel.POSITIVO
    assert SentimentLabel.from_string("NeGaTiVo") == SentimentLabel.NEGATIVO
    assert SentimentLabel.from_string("neutral") == SentimentLabel.NEUTRAL


def test_sentiment_label_from_string_invalid():
    with pytest.raises(ValueError, match="Unknown sentiment label"):
        SentimentLabel.from_string("unknown")


def test_sentiment_label_is_string_enum():
    assert isinstance(SentimentLabel.POSITIVO.value, str)
    assert SentimentLabel.POSITIVO == "positivo"


def test_cleaned_text_creation():
    ct = CleanedText("hello world")
    assert ct.value == "hello world"


def test_cleaned_text_empty_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        CleanedText("")


def test_cleaned_text_none_raises():
    with pytest.raises(ValueError):
        CleanedText(None)


def test_cleaned_text_equality():
    ct1 = CleanedText("same")
    ct2 = CleanedText("same")
    ct3 = CleanedText("different")
    assert ct1 == ct2
    assert ct1 != ct3


def test_cleaned_text_repr():
    ct = CleanedText("test")
    assert repr(ct) == "CleanedText('test')"
