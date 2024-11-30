import logging
import os
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger("django")

API_TOKEN = ""

class Command(BaseCommand):
    """Extracts all translatable strings and makes an API request with them."""

    help = "Extracts all translatable strings and makes an API request with them."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument("source_project", type=str, help="Source project name")

    def handle(self, *args, **kwargs):
        """Extracts all translatable strings and makes an API request with them."""
        import polib

        self.stdout.write(self.style.SUCCESS("Pulling translations..."))
        start_time = time.time()
        source_project = kwargs.get("source_project")
        # API request
        response = requests.post(
            "https://dj-polyglot.com/api/pull-translations/",
            data={"source_project": source_project},
            headers={"Authorization": API_TOKEN},
        )

        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to receive translatable strings. Status code: {response.status_code}, {response.content}. "
                    f"Time: {time.time() - start_time:.2f} seconds."
                )
            )
            return

        translations = response.json().get("translations", [])

        self.stdout.write(
            self.style.SUCCESS(f"Successfully received {len(translations)} translations from {source_project}")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully received {len(translations)} translatable strings in {time.time() - start_time:.2f} seconds."
            )
        )

        # Process translations for each locale
        self.stdout.write(self.style.SUCCESS("Adding translations to the PO files..."))

        locale_mapping = {"zh-hans": "zh_HAns", "zh-hant": "zh_HAnt", "pt-pt": "pt_PT"}

        for locale in [code for code, _ in settings.LANGUAGES]:
            if locale == "en":
                continue

            # Map locale to specific format if necessary
            locale = locale_mapping.get(locale, locale)

            logger.info(f"Processing locale: {locale}")
            po_file_path = os.path.join(settings.BASE_DIR, "locale", locale, "LC_MESSAGES", "django.po")

            if not os.path.exists(po_file_path):
                self.stdout.write(self.style.ERROR(f"File {po_file_path} not found"))
                continue

            # Open the PO file
            po_file = polib.pofile(po_file_path)

            # Update translations in PO file
            locale_translations = [t for t in translations if t.get("locale") == locale.lower()]
            for translation in locale_translations:
                msgid = translation.get("msgid")
                msgstr = translation.get("msgstr")
                entry = po_file.find(msgid)

                if entry:
                    entry.msgstr = msgstr
                else:
                    po_file.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

            # Remove obsolete entries
            for entry in po_file.obsolete_entries():
                po_file.remove(entry)

            # Save the PO file
            po_file.save(po_file_path)

        self.stdout.write(self.style.SUCCESS("Translations successfully added to the PO files."))
        self.stdout.write(
            self.style.SUCCESS(f"Pulling translations completed in {time.time() - start_time:.2f} seconds.")
        )
