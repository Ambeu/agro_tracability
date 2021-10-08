import csv
import datetime
from itertools import product

import folium
import pandas as pd
import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django_pandas.io import read_frame
from folium import plugins, raster_layers
from folium.plugins import MarkerCluster
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.views import APIView
from xhtml2pdf import pisa

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import ParcelleSerializer

@api_view(['GET'])
def map_parcelles(request):
    parcelles = Parcelle.objects.all().order_by('code')
    serializer = ParcelleSerializer(parcelles, many=True)
    nb_parcelles = parcelles.count()
    print(nb_parcelles)
    return Response(serializer.data)

def catre_parcelles(request):
    cooperatives = Cooperative.objects.all()
    context = {
        'cooperatives': cooperatives
    }
    return render(request, 'carte.html', context)

@api_view(['GET'])
def coop_parcelles(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    parcelle_coop = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    serializer = ParcelleSerializer(parcelle_coop, many=True)
    nb_parcelles = parcelle_coop.count()
    print(nb_parcelles)
    return Response(serializer.data)

def catre_parcelles_coop(request):
    return render(request, 'carte_coop.html')


from .forms import LoginForm
from .models import (
    Cooperative,
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    # Pepiniere,
    Activite,
    Region,
    # Campagne, Detail_Pepiniere, Detail_Retrait,
    # Formations,
)

from cooperatives.models import (
    Producteur,
    Parcelle,
    Planting,
    # Details_planting,
    Section,
    Sous_Section, Formation, Detail_Formation, DetailPlanting,
    Monitoring,
)

def connexion(request):
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid():
        username = login_form.cleaned_data.get("username")
        password = login_form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user != None:
            #utilisateur valide et actif(is_active=True)
            #"request.user == user"
            dj_login(request, user)
            group = request.user.groups.filter(user=request.user)[0]
            if group.name == "COOPERATIVES":
                messages.success(request, "Bienvenue : {}".format(username))
                return HttpResponseRedirect(reverse('cooperatives:dashboard'))
            elif group.name == "ADMIN":
                messages.success(request, "Bienvenue : {}".format(username))
                return HttpResponseRedirect(reverse('accueil'))
            elif group.name == "CLIENTS":
                messages.success(request, "Bienvenue : {}".format(username))
                return HttpResponseRedirect(reverse('clients:dashboard'))
            elif group.name == "AGROFORESTERIE":
                messages.success(request, "Bienvenue : {}".format(username))
                return HttpResponseRedirect(reverse('parif:dashboard'))
            elif group.name == "REFORESTATION":
                messages.success(request, "Bienvenue : {}".format(username))
                return HttpResponseRedirect(reverse('parif:dashboard'))
            else:
                messages.error(request, "Désolé vous n'estes pas encore enregistrer dans notre Sytème")
                return HttpResponseRedirect(reverse('connexion'))
        else:
            request.session['invalid_user'] = 1 # 1 == True
            messages.error(request, "Echec de Connexion, Assurez-vous d'avoir entrer le bon login et le bon Mot de Passe SVP !")
            return HttpResponseRedirect(reverse('connexion'))
    return render(request, 'parametres/login.html', {'login_form': login_form})

def loggout(request):
    logout(request)
    return HttpResponseRedirect(reverse('connexion'))

def index(request):
    cooperatives = Cooperative.objects.all()
    # communautes = Communaute.objects.all()
    # nb_communautes = Communaute.objects.all().count()
    nb_cooperatives = Cooperative.objects.all().count()
    nb_producteurs = Producteur.objects.all().count()
    nb_parcelles = Parcelle.objects.all().count()
    Superficie = Parcelle.objects.aggregate(total=Sum('superficie'))['total']
    Total_plant = Planting.objects.aggregate(total=Sum('plant_total'))['total']
    # plantings = Planting.objects.values("espece__libelle").filter(parcelle__producteur__cooperative_id=cooperative).annotate(plante=Sum('plant_recus'))

    context = {
        'nb_cooperatives': nb_cooperatives,
        'nb_producteurs': nb_producteurs,
        'nb_parcelles': nb_parcelles,
        'Superficie': Superficie,
        'Total_plant': Total_plant,
        # 'coop_nb_producteurs': coop_nb_producteurs,
        # 'coop_nb_parcelles': coop_nb_parcelles,
        # 'coop_superficie': coop_superficie,
        # 'plants': plants,
        # 'coop_plants_total': coop_plants_total,
    }
    return render(request, 'parametres/index.html', context)

def detail_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    section = Section.objects.filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.filter(section__cooperative_id=cooperative)
    # section_prod = Producteur.objects.all().filter(section_id__in=section).count()
    prod_section = Producteur.objects.filter(section_id__in=section).count()
    coop_nb_producteurs = Producteur.objects.filter(cooperative_id=cooperative).count()
    nb_formations = Formation.objects.filter(cooperative_id=cooperative).count()
    parcelles_section = Parcelle.objects.filter(producteur__section_id__in=section).count()
    coop_nb_parcelles = Parcelle.objects.filter(producteur__section__cooperative_id=cooperative).count()
    coop_superficie = Parcelle.objects.filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    section_superf = Parcelle.objects.filter(producteur__section_id__in=section).aggregate(total=Sum('superficie'))['total']
    section_plating = Planting.objects.filter(parcelle__producteur__section_id__in=section).aggregate(total=Sum('plant_recus'))['total']
    # plantings = Planting.objects.values("espece__libelle").filter(parcelle__producteur__cooperative_id=cooperative).annotate(plante=Sum('plant_recus'))
    coop_plants_total = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plante'))['total']

    context = {
        'cooperative': cooperative,
        'coop_nb_producteurs': coop_nb_producteurs,
        'coop_nb_parcelles': coop_nb_parcelles,
        'coop_superficie': coop_superficie,
        'nb_formations': nb_formations,
        'section': section,
        'sous_sections': sous_sections,
        'prod_section': prod_section,
        'parcelles_section': parcelles_section,
        # 'plantings': plantings,
        'coop_plants_total': coop_plants_total,
        'section_superf': section_superf,
        'section_plating': section_plating,
        # 'labels': labels,
        # 'data': data,
    }
    return render(request, 'Coop/cooperative.html', context)


