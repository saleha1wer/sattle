from django.db import models

class SatelliteImage(models.Model):
    image = models.ImageField(upload_to='satellite_images/', null=True, blank=True)
    country = models.CharField(max_length=100)
    coordinates = models.CharField(max_length=50, null=True, blank=True) 
    def __str__(self):
        return self.country

class Guess(models.Model):
    image = models.ForeignKey(SatelliteImage, on_delete=models.CASCADE)
    guessed_country = models.CharField(max_length=100)
    distance = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Guess for {self.image.country}"

    def is_correct(self):
        return self.distance == 0