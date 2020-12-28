from django.apps import AppConfig
from paperless_tika.signals import tika_consumer_declaration


class PaperlessTikaConfig(AppConfig):
    name = "paperless_tika"

    def ready(self):
        from documents.signals import document_consumer_declaration

        document_consumer_declaration.connect(tika_consumer_declaration)
        AppConfig.ready(self)
