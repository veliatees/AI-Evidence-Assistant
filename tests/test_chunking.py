import pytest
from app.chunking import chunk_text

test_text= ""
test_text2= "abc"    
test_text3= "one two three four five six"
    
def test_chunk_text_returns_empty_list_for_empty_text():
    result= chunk_text(text=test_text, chunk_size=3, overlap=2)

    if result==[]:
        return "The text is empty"

def test_chunk_text_returns_single_chunk_when_text_is_short():
    result2= chunk_text(text=test_text2, chunk_size=3, overlap=2)
    if len(result2)<3:
        return test_text2
    
#def test_chunk_text_uses_overlap_between_chunks():
    result3= chunk_text(text=test_text3, chunk_size=3, overlap=2)
    