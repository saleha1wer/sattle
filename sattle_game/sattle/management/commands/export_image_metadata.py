import json
from django.core.management.base import BaseCommand
from sattle.models import SatelliteImage

class Command(BaseCommand):
    help = 'Exports satellite image metadata to a dictionary'

    def handle(self, *args, **options):
        image_metadata = {}

        for satellite_image in SatelliteImage.objects.all():
            filename = satellite_image.image.name.split('/')[-1]
            country = satellite_image.country
            coordinates = satellite_image.coordinates
            image_metadata[filename] = [country, coordinates]

        # Print the dictionary as a JSON-formatted string
        print(json.dumps(image_metadata))
