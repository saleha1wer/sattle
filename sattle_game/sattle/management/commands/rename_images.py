from django.core.management.base import BaseCommand
from sattle.models import SatelliteImage
import os
import uuid

class Command(BaseCommand):
    help = 'Rename all satellite images to random names.'

    def handle(self, *args, **kwargs):
        for image in SatelliteImage.objects.all():
            file_path = image.image.path
            folder_name = os.path.dirname(file_path)
            file_extension = os.path.splitext(file_path)[1]
            # Generate a new random file name using UUID
            new_file_name = f"{uuid.uuid4()}{file_extension}"
            new_file_path = os.path.join(folder_name, new_file_name)
            os.rename(file_path, new_file_path)
            image.image.name = os.path.join(os.path.basename(folder_name), new_file_name)
            image.save()
            self.stdout.write(self.style.SUCCESS(f'Renamed {file_path} to {new_file_name}'))
