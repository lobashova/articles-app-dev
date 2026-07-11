import fitz  # PyMuPDF
import requests
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    # Читаем первые 2 страницы (обычно там метаданные)
    for page in doc.pages(0, 2):
        text += page.get_text()
    return text

def extract_doi_from_text(text):
    # Регулярное выражение для поиска стандартного DOI
    match = re.search(r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b', text, re.IGNORECASE)
    if match:
        return match.group(1).rstrip('.')
    return None

def get_metadata_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        # Добавляем таймаут, чтобы сервер не зависал, если Crossref недоступен
        response = requests.get(url, timeout=5) 
        if response.status_code == 200:
            data = response.json()['message']
            return {
                "title": data.get('title', [None])[0],
                "year": data.get('published', {}).get('date-parts', [[None]])[0][0],
                "journal": data.get('container-title', [None])[0],
                "doi": doi
            }
    except Exception as e:
        print(f"Ошибка при запросе к Crossref: {e}")
    return None