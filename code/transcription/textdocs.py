from docx import Document
from PyPDF2 import PdfReader

# Read in a .docx file and return the text:
def read_docx(filename):
    doc = Document(filename)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return ' '.join(full_text)


# Read in a .pdf file and return the text:
def read_pdf(filename):
    pdf = PdfReader(filename)
    full_text = []
    for page in pdf.pages:
        full_text.append(page.extract_text())
    return ' '.join(full_text)


# Read in a .txt file and return the text:
def read_txt(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        full_text = file.read()
    return full_text.replace('\n', ' ')