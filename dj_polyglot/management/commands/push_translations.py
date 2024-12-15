import logging
import os

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger("django")


class Command(BaseCommand):
    """Command to extract all translatable strings and send them to an API endpoint."""

    help = "Extracts all translatable strings and makes an API request with them."

    def handle(self, *args, **kwargs):
        """Handle the command."""
        import polib

        translatable_strings = []

        locale_path = os.path.join(settings.BASE_DIR, "locale")

        # Iterate over all .po files in the locale directory
        for root, dirs, files in os.walk(locale_path):
            for file in files:
                logger.info(f"Processing file: {file}")
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    po_file = polib.pofile(po_file_path)

                    for entry in po_file:
                        if entry.msgid:
                            translatable_strings.append(
                                {"msgid": entry.msgid, "locale": os.path.basename(root), "context": entry.msgctxt}
                            )

        logger.info(f"Found {len(translatable_strings)} translatable strings.")
        logger.info("Pusing translatable strings to the API...")
        data = {"translations": translatable_strings, "source_project": settings.DJ_POLYGLOT_PROJECT}
        service_url = "https://dj-polyglot.com"

        response = requests.post(
            f"{service_url}/api/push-translations/",
            json=data,
            headers={"Authorization": f"Token {settings.DJ_POLYGLOT_KEY}"},
        )

        # Check the response status
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("Successfully pushed translatable strings."))
        else:
            self.stdout.write(
                self.style.ERROR(f"Failed to pushed translatable strings. Status code: {response.status_code}")
            )
