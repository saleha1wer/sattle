from django.core.management.base import BaseCommand
from sattle.models import SatelliteImage

class Command(BaseCommand):
    help = 'Review and optionally delete satellite images.'

    def handle(self, *args, **options):
        # Grouping images by country
        countries = SatelliteImage.objects.values_list('country', flat=True).distinct()
        total_countries = len(countries)

        for country in countries:
            self.stdout.write(f"Reviewing images for country: {country}")
            images_for_country = SatelliteImage.objects.filter(country=country)
            
            for image in images_for_country:
                self.stdout.write(f"Image URL: {image.image.url}")
                
            decision = input("Do you want to delete this image? (y/n): ")
 
            if decision.lower() == 'y':
                for image in images_for_country:
                    image.image.delete()  # This will delete the image file
                    image.delete()  # This will delete the database record
                    self.stdout.write(f"Deleted image")

            total_countries -= 1
            self.stdout.write(f"\n{total_countries} unique countries with images left to review.\n")

        self.stdout.write("Review process completed!")
