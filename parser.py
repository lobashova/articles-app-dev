import fitz  # PyMuPDF
import requests

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    # Читаем первые 2 страницы (обычно там метаданные)
    for page in doc.pages(0, 2):
        text += page.get_text()
    return text

def get_metadata_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['message']
        return {
            "title": data.get('title', [None])[0],
            "year": data.get('published', {}).get('date-parts', [[None]])[0][0],
            "journal": data.get('container-title', [None])[0]
        }
    return None