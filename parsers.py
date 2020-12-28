import os
import subprocess
import tika
import requests
import dateutil.parser

from PIL import ImageDraw, ImageFont, Image
from django.conf import settings

from documents.parsers import DocumentParser, ParseError
from paperless_tesseract.parsers import RasterisedDocumentParser
from tika import parser


class TikaDocumentParser(DocumentParser):
    """
    This parser sends documents to a local tika server
    """

    def get_thumbnail(self, document_path, mime_type):
        self.log("info", f"[TIKA_THUMB] Generating thumbnail for{str(document_path)}")
        archive_path = self.archive_path

        out_path = RasterisedDocumentParser.get_thumbnail(self, archive_path, mime_type)

        return out_path

    def parse(self, document_path, mime_type):
        self.log("info", f"[TIKA_PARSE] Sending {str(document_path)} to Tika server")
        parsed = parser.from_file(document_path)

        try:
            content = parsed["content"].strip()
        except:
            content = ""

        try:
            creation_date = dateutil.parser.isoparse(
                parsed["metadata"]["Creation-Date"]
            )
        except:
            creation_date = None

        archive_path = os.path.join(self.tempdir, "convert.pdf")
        convert_to_pdf(self, document_path, archive_path)

        self.archive_path = archive_path
        self.date = creation_date
        self.text = content


def convert_to_pdf(self, document_path, pdf_path):
    pdf_path = os.path.join(self.tempdir, "convert.pdf")
    gotenberg_server = os.getenv("PAPERLESS_GOTENBERG", "http://localhost:3000")
    url = gotenberg_server + "/convert/office"

    self.log(
        "info", f"[TIKA] Converting {str(document_path)} to PDF as {str(pdf_path)}"
    )
    files = {"files": open(document_path, "rb")}
    headers = {}
    response = requests.post(url, files=files, headers=headers)

    response.raise_for_status()  # ensure we notice bad responses

    file = open(pdf_path, "wb")
    file.write(response.content)
    file.close()
