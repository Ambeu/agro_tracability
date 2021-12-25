from django import forms
from django.contrib import admin
from django.http import request
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Cooperative,
    Section,
    Sous_Section,
    Producteur,
    Parcelle,
    Planting,
    DetailPlanting,
    Monitoring,
    Formation,
    Detail_Formation,
)

class SouSectionAdmin(admin.TabularInline):
    model = Sous_Section
    extra = 0

class CooperativeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "sigle", "contacts"]

class SectionResource(resources.ModelResource):
    class Meta:
        model = Section

class SectionAdmin(ImportExportModelAdmin):
    resource_class = SectionResource
    list_display = ["id", "libelle", "responsable", "cooperative"]
    inlines = [SouSectionAdmin]

class ProdResource(resources.ModelResource):
    class Meta:
        model = Producteur

class ProducteurAdmin(ImportExportModelAdmin):
    list_display = ["id", "code", "nom", "section", "localite"]
    list_filter = ["cooperative__sigle", "section__libelle", ]
    search_fields = ["code", "nom", "contacts", "section__libelle", ]
    resource_class = ProdResource

class ParcelleResource(resources.ModelResource):
    class Meta:
        model = Parcelle

class ParcelleAdmin(ImportExportModelAdmin):
    list_display = ["id", "code", "producteur", "acquisition", "culture", "certification", "coordonnees"]
    list_filter = ["producteur__section__libelle", "producteur__cooperative",]
    search_fields = ["code", "producteur__nom", "latitude", "longitude", "superficie"]

class DetailPlantingAdmin(admin.TabularInline):
   model = DetailPlanting
   extra = 0

class DetailPlantingResource(resources.ModelResource):
    class Meta:
        model = DetailPlanting

class DetailPlantingAdmin(ImportExportModelAdmin):
    resource_class = DetailPlantingResource

class MinitoringAdmin(admin.TabularInline):
   model = Monitoring
   fields = ['espece', 'mort', 'remplace', 'date', 'mature', 'observation']
   list_display = ['espece', 'mort', 'remplace', 'date', 'mature', 'observation']
   extra = 0

class PlantingAdmin(ImportExportModelAdmin):
   fields = ('parcelle', 'projet', "campagne", "nb_plant_exitant", "plant_recus", "plant_total", "date")
   list_display = ('pk', 'parcelle','projet', "campagne", "nb_plant_exitant", "plant_recus", "plant_total", "date")
   list_display_links = ('parcelle',)
   list_filter = ["parcelle__producteur__cooperative", ]
   readonly_fields = ["plant_total"]
   inlines = [MinitoringAdmin]

# admin.site.register(Cooperative, CooperativeAdmin)
admin.site.register(Section, SectionAdmin)
# admin.site.register(Sous_Section)
admin.site.register(Formation)
# admin.site.register(Stat)
admin.site.register(Detail_Formation)
admin.site.register(Producteur, ProducteurAdmin)
admin.site.register(Parcelle, ParcelleAdmin)
admin.site.register(Planting, PlantingAdmin)
admin.site.register(DetailPlanting, DetailPlantingAdmin)
# admin.site.register(Pepiniere, PepiniereAdmin)
# admin.site.register(Retrait_plant, RetraitPlantAdmin)
# Register your models here.
