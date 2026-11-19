from src.ingestion.pdf_loader import DocumentPage
from src.ingestion.chunker import chunk_documents

def test_chunk_metadata_and_non_empty():
    pages = [DocumentPage(text="Birinci paragraf.\n\nİkinci paragraf.", source="test.pdf", page=1)]
    chunks = chunk_documents(pages, chunk_size=512, overlap=64)
    assert len(chunks) == 1
    assert chunks[0].source == "test.pdf"
    assert chunks[0].page == 1

def test_chunk_overlap_works_within_same_page():
    # Gerçekçi cümlelerden oluşan uzun bir metin
    long_text = " ".join([f"Bu {i}. örnek cümledir." for i in range(30)])
    pages = [DocumentPage(text=long_text, source="test.pdf", page=2)]
    chunks = chunk_documents(pages, chunk_size=200, overlap=40)
    assert len(chunks) > 1
    # İlk chunk'ın son kelimesi ikinci chunk'ın içinde (overlap) yer almalı
    last_word_of_first = chunks[0].text.split()[-1]
    assert last_word_of_first in chunks[1].text