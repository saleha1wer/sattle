import os
from django.core.management.base import BaseCommand
from sattle.models import SatelliteImage
from django.core.files import File

class Command(BaseCommand):
    help = 'Imports satellite images from local folder to the database'

    def handle(self, *args, **options):
        images_directory = "/home/salehalwer/root/sattle/images"

        for filename in os.listdir(images_directory):
            if filename.endswith('.png'):
                # Extracting latitude, longitude, and country from filename
                parts = filename.replace('.png', '').split(',')
                latitude, longitude = parts[0], parts[1]
                country = "_".join(parts[2:]).replace('_', ' ')  # Extracting country name and converting underscores back to spaces
                
                # Constructing full path
                full_path = os.path.join(images_directory, filename)

                # Create a new SatelliteImage instance
                satellite_image = SatelliteImage()
                satellite_image.coordinates = f"{latitude},{longitude}"
                satellite_image.country = country

                # Open and attach the image file
                with open(full_path, 'rb') as image_file:
                    satellite_image.image.save(filename, File(image_file), save=True)

                self.stdout.write(self.style.SUCCESS(f'Successfully imported {filename}'))
