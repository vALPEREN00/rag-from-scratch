from dataclasses import dataclass
from pathlib import Path
import re
import pdfplumber

@dataclass
class DocumentPage:
    text: str
    source: str
    page: int

def clean_text(text: str) -> str:
    """PDF'ten çıkan metindeki bozuk boşlukları ve fazla satır sonlarını temizler."""

    text = re.sub(r"\n?\d+\s+A practical guide to building agents\s*", "", text)
    text = re.sub(r"[\t]+"," ",text) # Satır içi fazla boşlukları tek boşluğa indirir.
    text = re.sub(r"\n{3,}", "\n\n", text) # 3 veya daha fazla art arda gelen satır sonunu 2'ye (paragraf sınırına) indirir.
    return text.strip()

def load_pdf(file_path: str | Path) -> list[DocumentPage]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF bulunamadı: {path}")

    pages: list[DocumentPage] = []
    with pdfplumber.open(path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text(x_tolerance=2) or ""
            cleaned = clean_text(raw_text)
            if cleaned:
                pages.append(
                    DocumentPage(
                        text=cleaned,
                        source=path.name,
                        page=page_index,
                    )
                )
    return pages

if __name__ == "__main__":
    docs = load_pdf("data/raw/openai_agents_guide.pdf")
    print(f"Toplam okunan dolu sayfa: {len(docs)}")
    print(f"Örnek metadata -> Kaynak: {docs[0].source}, Sayfa: {docs[0].page}")
    print("-" * 50)
    print(docs[2].text[:500])