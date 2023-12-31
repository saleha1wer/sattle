# Generated by Django 4.0.6 on 2023-09-25 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sattle', '0005_userscore'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalHighScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('score', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
