# Generated by Django 3.1.7 on 2022-01-05 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0003_auto_20220105_0848'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pepiniere',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=250, verbose_name='DELEGATION REGIONALE')),
                ('ville', models.CharField(max_length=250, verbose_name='VILLE')),
                ('site', models.CharField(max_length=250, verbose_name='SITE')),
                ('latitude', models.CharField(blank=True, max_length=10, null=True)),
                ('longitude', models.CharField(blank=True, max_length=10, null=True)),
                ('fournisseur', models.CharField(max_length=255, verbose_name='NOM ET PRENOMS FOURNISSEUR')),
                ('contacts_fournisseur', models.CharField(blank=True, max_length=50, null=True, verbose_name='CONTACTS FOURNISSEUR')),
                ('technicien', models.CharField(max_length=255, verbose_name='NOM ET PRENOMS TECHNICIEN')),
                ('contacts_technicien', models.CharField(blank=True, max_length=50, null=True, verbose_name='CONTACTS TECHNICIEN')),
                ('superviseur', models.CharField(max_length=255, verbose_name='NOM ET PRENOMS TECHNICIEN')),
                ('contacts_superviseur', models.CharField(blank=True, max_length=50, null=True, verbose_name='CONTACTS SUPERVISUER')),
                ('sachet_recus', models.PositiveIntegerField(default=0, verbose_name='QTE TOTAL SACHET RECU')),
                ('production_plant', models.PositiveIntegerField(default=0, verbose_name='PLANTS A PRODUIRE')),
                ('production_realise', models.PositiveIntegerField(default=0, verbose_name='REALISATION')),
                ('pourcentage_prod', models.PositiveIntegerField(default=0, verbose_name='POURCENTAGE DE PRODUCTION')),
                ('plant_mature', models.PositiveIntegerField(default=0, verbose_name='NBRE PLANT MATURE')),
                ('plant_retire', models.PositiveIntegerField(default=0, verbose_name='NBRE TOTAL PLANT RETIRE')),
                ('add_le', models.DateTimeField(auto_now_add=True)),
                ('update_le', models.DateTimeField(auto_now=True)),
                ('campagne', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parametres.campagne')),
                ('projet', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parametres.projet')),
            ],
            options={
                'verbose_name': 'pépinière',
                'verbose_name_plural': 'PEPINIERES',
            },
        ),
        migrations.CreateModel(
            name='Semence_Pepiniere',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production', models.PositiveIntegerField(default=0, verbose_name='NB PLANTS A PRODUIRE')),
                ('qte_recu', models.PositiveIntegerField(default=0, verbose_name='QTE RECU')),
                ('date', models.DateField(verbose_name='DATE RECEPTION')),
                ('origine', models.CharField(max_length=255, verbose_name='ORIGINE')),
                ('details', models.TextField(blank=True, null=True)),
                ('add_le', models.DateTimeField(auto_now_add=True)),
                ('update_le', models.DateTimeField(auto_now=True)),
                ('espece_recu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.espece')),
                ('pepiniere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.pepiniere')),
            ],
            options={
                'verbose_name': 'détail semence reçu',
                'verbose_name_plural': 'DETAILS SEMENCES RECUS',
            },
        ),
    ]
