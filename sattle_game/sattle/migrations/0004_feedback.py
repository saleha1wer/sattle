# Generated by Django 4.0.6 on 2023-09-22 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sattle', '0003_guess_correct_guess_correct_country_guess_direction_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user_identifier', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
