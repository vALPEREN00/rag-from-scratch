from dataclasses import dataclass
import re
from src.ingestion.pdf_loader import DocumentPage, load_pdf

@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str
    page: int
    chunk_index: int

def split_into_units(text:str) -> list[str]:
    """Metni önce paragraf/satır sınırlarından, çok uzunsa cümle sınırlarından böler."""

    paragraph = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    units: list[str] = []
    for para in paragraph:
        #Tek bir paragraf çok uzunsa, cümle sonlarından böl
        if len(para) > 400:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            units.extend([s.strip() for s in sentences if s.strip()])
        else:
            units.append(para)
    return units


def chunk_documents(
        pages: list[DocumentPage],
        chunk_size: int= 512,
        overlap: int = 64
) -> list[Chunk]:
    """
    Sayfaları paragraf/cümle sınırlarını koruyarak chunk'lara böler.
    Her chunk'a kaynak dosya ve sayfa numarasını metadata olarak ekler.
    """
    if overlap >= chunk_size:
        raise ValueError("Overlap değeri, chunk_size'dan küçük olmalıdır.")

    chunks: list[Chunk] = []
    global_idx = 0

    for page_doc in pages:
        units = split_into_units(page_doc.text)
        current_text = ""

        for unit in units:
            #Mevcut chunk'a yeni ünite sığıyorsa ekle
            candidate = f"{current_text}\n{unit}".strip() if current_text else unit
            if len(candidate) <= chunk_size:
                current_text = candidate
            else:
                #Mevcut birikmiş metni chunk olarak kaydet
                if current_text:
                    chunks.append(
                        Chunk(
                            chunk_id=f"{page_doc.source}_p{page_doc.page}_c{global_idx}",
                            text= current_text,
                            source= page_doc.source,
                            page=page_doc.page,
                            chunk_index=global_idx
                        )
                    )
                    global_idx += 1

                #Overlap: önceki chunk'ın sonundan kelime bütünlüğünü bozmadan ekle
                overlap_text = current_text[-overlap:].strip() if overlap > 0 and current_text else ""
                if overlap_text and " " in overlap_text:
                    overlap_text = overlap_text.split(" ", 1)[1] 

                current_text = f"{overlap_text}\n{unit}".strip() if overlap_text else unit


        #Sayfa sonunda kalan parçayı kaydet
        if current_text:
            chunks.append(
                Chunk(
                    chunk_id=f"{page_doc.source}_p{page_doc.page}_c{global_idx}",
                    text=current_text,
                    source=page_doc.source,
                    page=page_doc.page,
                    chunk_index=global_idx
                )
            )
            global_idx += 1

    return chunks

if __name__ == "__main__":
    pages = load_pdf("data/raw/openai_agents_guide.pdf")
    chunks = chunk_documents(pages, chunk_size=512, overlap=64)

    avg_len = sum(len(c.text) for c in chunks) / len(chunks)
    print(f"Toplam sayfa: {len(pages)}")
    print(f"Toplam chunk: {len(chunks)}")
    print(f"Ortalama chunk uzunluğu: {avg_len:.1f} karakter")
    print("=" * 60)
    print(f"[Chunk 3] ID: {chunks[3].chunk_id} | Sayfa: {chunks[3].page}")
    print(chunks[3].text)
    print("-" * 60)
    print(f"[Chunk 4] ID: {chunks[4].chunk_id} | Sayfa: {chunks[4].page}")
    print(chunks[4].text)
