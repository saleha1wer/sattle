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
    correct_country = models.CharField(max_length=100, null=True, blank=True)
    distance = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_identifier = models.CharField(max_length=255, null=True, blank=True)
    correct = models.BooleanField(null=True, blank=True)
    direction = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"Guess for {self.image.country}"

    def is_correct(self):
        return self.distance == 0

class WebsiteStats(models.Model):
    total_guesses = models.IntegerField(default=0)
    total_correct_guesses = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)

    # This ensures we only ever have one row in this table
    def save(self, *args, **kwargs):
        self.pk = 1
        super(WebsiteStats, self).save(*args, **kwargs)

class Feedback(models.Model):
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_identifier = models.CharField(max_length=255, null=True, blank=True)
    response_info = models.CharField(max_length=255, null=True, blank=True)  # New field for email or Discord


class UserScore(models.Model):
    user_identifier = models.CharField(max_length=255, unique=True)
    high_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user_identifier} - {self.high_score}"

class GlobalHighScore(models.Model):
    name = models.CharField(max_length=255)
    message = models.TextField()
    score = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)