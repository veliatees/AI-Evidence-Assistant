def chunk_text(text:str, chunk_size: int = 120, overlap:int = 20)->list[str]:
    words= text.split()
    if not words:
        return[]

    if overlap>=chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    
    chunks=[]
    start= 0
    while start<len(words):
        end= start+chunk_size
        chunk_word= words[start:end]
        chunks.append(" ".join(chunk_word))

        if end>=len(words):
            break
        start= end-overlap
    return chunks