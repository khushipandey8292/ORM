# Generated by Django 5.1.4 on 2025-05-13 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_app', '0007_seatavailability'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SeatAvailability',
        ),
    ]
