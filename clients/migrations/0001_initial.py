# Generated by Django 3.2.7 on 2021-09-30 11:07

import clients.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sigle', models.CharField(max_length=500, verbose_name='NOM / SIGLE')),
                ('contacts', models.CharField(max_length=50, verbose_name='CONTACTS')),
                ('libelle', models.CharField(max_length=250, verbose_name='NOM')),
                ('pays', django_countries.fields.CountryField(max_length=2)),
                ('adresse', models.CharField(blank=True, max_length=250, verbose_name='ADRESSE')),
                ('telephone1', models.CharField(max_length=50)),
                ('telephone2', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=120, verbose_name='ADRESSE EMAIL')),
                ('siteweb', models.CharField(blank=True, max_length=120, verbose_name='SITE WEB')),
                ('logo', models.ImageField(blank=True, upload_to=clients.models.upload_logo_site, verbose_name='Logo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'CLIENTS',
            },
        ),
    ]
