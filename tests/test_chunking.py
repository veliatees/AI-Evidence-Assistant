import pytest
from app.chunking import chunk_text
    
def test_chunk_text_returns_empty_list_for_empty_text():
    result= chunk_text(text="", chunk_size=3, overlap=2)
    assert result == []

def test_chunk_text_returns_single_chunk_when_text_is_short():
    result= chunk_text(text="abc", chunk_size=3, overlap=2)
    assert result == ["abc"]
    
def test_chunk_text_uses_overlap_between_chunks():
    result= chunk_text(text="one two three four five six", chunk_size=3, overlap=1)
    assert result == [
        "one two three",
        "three four five",
        "five six",
    ]

def test_chunk_text_raises_error_when_overlap_is_too_large():
    with pytest.raises(ValueError):
        chunk_text(text= "one two three", chunk_size=3, overlap=3)