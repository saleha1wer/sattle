from django.core.management.base import BaseCommand
import json
from sattle.models import SatelliteImage
import os
from django.core.files import File

class Command(BaseCommand):
    help = 'Populate database from a given dictionary in a file'

    def add_arguments(self, parser):
        parser.add_argument('--image_metadata_file', type=str, help='Path to the file containing the image metadata in JSON format.')

    def handle(self, *args, **kwargs):
        file_path = kwargs['image_metadata_file']

        with open(file_path, 'r') as file:
            image_metadata = json.load(file)

        images_directory = "/home/salehalwer/root/sattle/sattle_game/media/satellite_images/"
        
        for filename, data in image_metadata.items():
            country, coordinates = data

            if not SatelliteImage.objects.filter(image__contains=filename).exists():
                full_path = os.path.join(images_directory, filename)
                
                satellite_image = SatelliteImage()
                satellite_image.coordinates = coordinates
                satellite_image.country = country

                with open(full_path, 'rb') as image_file:
                    satellite_image.image.save(filename, File(image_file), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {filename}'))

