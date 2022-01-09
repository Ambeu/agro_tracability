# Generated by Django 3.1.7 on 2022-01-05 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0003_auto_20220105_0848'),
        ('cooperatives', '0006_auto_20220105_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoring',
            name='observation',
            field=models.ManyToManyField(related_name='cooperatives_monitoring_observation', to='parametres.ObsMonitoring'),
        ),
    ]
