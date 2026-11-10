from pypdf import PdfReader
from docx import Document


class TextExtractionService:
    def extract_text(self,path):
        prefix = path.split(".")[-1]
        if prefix == "pdf" or prefix == "PDF":
            reader = PdfReader(path)
            extracted_txt = ""
            for p in reader.pages:
                tmp = p.extract_text(extraction_mode="layout")

                if tmp:
                    extracted_txt += tmp + "\n"
            return extracted_txt
        doc = Document(path)
        extracted_txt = ""
        for paragraph in doc.paragraphs:
            if paragraph.text:
                extracted_txt += paragraph.text + "\n"
        return extracted_txt