from django.core.management.base import BaseCommand
from sattle.models import SatelliteImage

COUNTRY_CENTER_COORDS = {
    'Aruba': (12.5013629, -69.9618475),
    'Afghanistan': (33.7680065, 66.2385139),
    # ... (rest of your dictionary)
}
country_names = set(COUNTRY_CENTER_COORDS.keys())

class Command(BaseCommand):
    help = 'Check satellite images for country name mismatches'

    def handle(self, *args, **kwargs):
        mismatched_images = []

        for image in SatelliteImage.objects.all():
            # Check if the country name matches exactly
            if image.country in country_names:
                continue

            # Check if the issue is just capitalization of the first letter
            capitalized_country = image.country.capitalize()
            if capitalized_country in country_names:
                image.country = capitalized_country
                image.save()
                continue

            # If it doesn't match any, store it in a list
            mismatched_images.append(image.country)

        # Print all image's names that do not match
        if mismatched_images:
            self.stdout.write(self.style.ERROR('Mismatched country names:'))
            for name in mismatched_images:
                self.stdout.write(self.style.ERROR(name))
        else:
            self.stdout.write(self.style.SUCCESS('All satellite images match country names!'))
