import csv
import datetime
from itertools import product
from django.forms.fields import DateField
from django.forms.forms import Form
from django.template.loader import render_to_string
from django.template.context import Context

import folium
import pandas as pd
from django.core import serializers
import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader,RequestContext
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

from .serializers import ParcelleSerializer, PepiniereSerializer, PlantingSerializer, DetailsPlantingSerializer, SectionSerializer
from cooperatives.models import Planting, DetailPlanting



class PlantingParifApiView(ListAPIView):
    queryset = Planting.objects.all()
    p_count = queryset.count()
    print(p_count)
    serializer_class = PlantingSerializer

class DetailPlantingParifApiView(ListAPIView):
    queryset = DetailPlanting.objects.all()
    p_count = queryset.count()
    print(p_count)
    serializer_class = DetailsPlantingSerializer

@api_view(['GET'])
def map_parcelles(request):
    parcelles = Parcelle.objects.all().order_by('code')
    serializer = ParcelleSerializer(parcelles, many=True)
    nb_parcelles = parcelles.count()
    print(nb_parcelles)
    return Response(serializer.data)


@api_view(['GET'])
def map_cooperative(request):

    id = request.GET.get('id')

    if id != "":
        cooperative = get_object_or_404(Cooperative, id=id)
        parcelle_coops = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
        nb_parcelles = parcelle_coops
        section_coops = Section.objects.filter(cooperative_id=cooperative)

        sections = serializers.serialize('json',section_coops)

        context ={
            "cooperative":cooperative,
            "parcelle_coops":parcelle_coops,
            "nb_parcelles":nb_parcelles,
        }

        templateStr = render_to_string("cooperatives/carte_coop.html", context)
        return JsonResponse({'templateStr':templateStr,'id':id,'sections':sections},safe=False)

    else:
        cooperatives = Cooperative.objects.all()
        context = {
            'cooperatives': cooperatives
        }
        templateStr = render_to_string("cooperatives/carte_coop.html", context)
        return JsonResponse({'templateStr':templateStr,'id':""},safe=False)


@api_view(['GET'])
def map_section(request):

    id = request.GET.get('id')
    id_coop = request.GET.get('id_coop')

    if id != "" and id_coop != "":
        section_coop = Section.objects.filter(id=id)

        context ={
            "section_coop":section_coop,
        }
        templateStr = render_to_string("cooperatives/carte_section.html", context)
        return JsonResponse({'templateStr':templateStr,'id':id,'id_coop':id_coop},safe=False)

    elif id == "" and id_coop !="":
        cooperative = get_object_or_404(Cooperative, id=id_coop)
        parcelle_coops = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
        nb_parcelles = parcelle_coops

        context ={
            "cooperative":cooperative,
            "parcelle_coops":parcelle_coops,
            "nb_parcelles":nb_parcelles,
        }

        templateStr = render_to_string("cooperatives/carte_coop.html", context)
        return JsonResponse({'templateStr':templateStr,'id':id,'id_coop':id_coop},safe=False)


    

@api_view(['GET'])
def api_detail_cooperative(request,id):
    cooperative = get_object_or_404(Cooperative, id=id)
    queryset = Planting.objects.filter(producteur__cooperative_id=id)
    p_count = queryset.count()
    serializer = PlantingSerializer(queryset, many=True)
    
    print(p_count)
    return Response(serializer.data)

@api_view(['GET'])
def map_plantings_espece_old(request, id):
    queryset = DetailPlanting.objects.filter(planting_id=id)
    p_count = queryset.count()
    print(p_count)

    data = serializers.serialize('json', queryset)
   
    return JsonResponse({'data':data},safe=False)

from django.contrib.auth.models import Group
def map_plantings_espece(request,id):
    groups = []
    user = request.user
    if user.is_authenticated:
        groups = list(user.groups.values_list('name', flat=True))

    queryset = DetailPlanting.objects.filter(planting_id=id)
    planting = Planting.objects.get(id = id)

    t_planting = DetailPlanting.objects.filter(planting_id=planting).aggregate(total=Sum('nb_plante'))['total']

    print(planting)
    p_count = queryset.count()
    print(p_count)

    context = {
        't_planting':t_planting,
        'groups': groups,
        'especes':queryset,
        'planting':planting
    }

    #data = serializers.serialize('json', queryset)
   
    return render(request,'cooperatives/detail_espece.html',context)


def catre_parcelles(request):
    cooperatives = Cooperative.objects.all()
    context = {
        'cooperatives': cooperatives
    }
    return render(request, 'carte.html', context)

@api_view(['GET'])
def coop_parcelles(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    parcelle_coop = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative)
    serializer = PlantingSerializer(parcelle_coop, many=True)
    nb_parcelles = parcelle_coop.count()
    print(nb_parcelles)
    return Response(serializer.data)

@api_view(['GET'])
def section_parcelles(request, id=None):
    section = get_object_or_404(Section, id=id)
    parcelle_coop = Planting.objects.filter(parcelle__producteur__section_id=section)
    serializer = PlantingSerializer(parcelle_coop, many=True)
    nb_parcelles = parcelle_coop.count()
    print(nb_parcelles)
    return Response(serializer.data)

@api_view(['GET'])
def coop_section(request, id_coop=None):
    cooperative = get_object_or_404(Cooperative, id=id_coop)
    section_coop = Section.objects.filter(cooperative_id=cooperative)
    serializer = SectionSerializer(section_coop, many=True)
    nb_sections = section_coop.count()
    print(nb_sections)
    return Response(serializer.data)

# @api_view(['GET'])
# def Planting_map(request):
#     # cooperative = get_object_or_404(Cooperative, id=id)
#     plantings = Planting.objects.all()
#     serializer = DetailPlantingSerializer(plantings, many=True)
#     nb_plantings = plantings.count()
#     print(nb_plantings)
#     return Response(serializer.data)

def catre_parcelles_coop(request):
    return render(request, 'carte_coop.html')


from .forms import LoginForm, PepiniereForm, SemenceForm
from .models import (
    Cooperative,
    Espece,
    Pepiniere,
    Semence_Pepiniere,
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


#secteur pepiniere semences

def pepiniere(request):
    pepinieres = Pepiniere.objects.all()
    pepiForm = PepiniereForm()
    activate = "pepiniere"
    if request.method == 'POST':
        pepiForm = PepiniereForm(request.POST, request.FILES)
        if pepiForm.is_valid():
            pepiniere = pepiForm.save(commit=False)
            pepiniere = pepiniere.save()
            print(pepiniere)
        messages.success(request, "Site Pépinière Ajouté avec succès")
        return HttpResponseRedirect(reverse('pepinieres'))

    context = {
        'pepinieres': pepinieres,
        'pepiForm': pepiForm,
        'activate':activate
    }
    return render(request, 'parametres/pepinieres.html', context)


def catre_pepiniere(request):
    pepinieres = Pepiniere.objects.all()
    context = {
        'pepinieres': pepinieres,
    }
    return render(request, 'parametres/carte_pepiniere.html', context)

@api_view(['GET'])
def map_pepinieres(request):
    pepinieres = Pepiniere.objects.all().order_by('id')
    serializer = PepiniereSerializer(pepinieres, many=True)
    nb_parcelles = pepinieres.count()
    print(nb_parcelles)
    return Response(serializer.data)


def Editpepiniere(request, id=None):
    instance = get_object_or_404(Pepiniere, id=id)
   
    pepiForm = PepiniereForm(request.POST or None, request.FILES or None, instance=instance)
        
    if pepiForm.is_valid():
        pepiniere = pepiForm.save(commit=False)
        pepiniere.save()
        messages.success(request, "Modification Effectuée Avec Succès", extra_tags='html_safe')
        return HttpResponseRedirect(reverse('pepinieres'))
        


    context = {
        "instance": instance,
        "pepiForm": pepiForm,
    }

    return render(request, "cooperatives/edit_pepiniere.html", context)

def detail_pepiniere(request, id=None):
    #cooperative = Cooperative.objects.get(user_id=request.user.id)
    instance = get_object_or_404(Pepiniere, id=id)
    semences = Semence_Pepiniere.objects.all().filter(pepiniere_id=instance)
    total_plants_a_produire = Semence_Pepiniere.objects.all().filter(pepiniere_id=instance).aggregate(total=Sum('production'))['total']


    semenceForm = SemenceForm()
    #print(semenceForm)

    if request.method == 'POST':
        semenceForm = SemenceForm(request.POST, request.FILES)
        if semenceForm.is_valid():
            semence_recu = semenceForm.save(commit=False)
            semence_recu.pepiniere_id = instance.id
            semence_recu = semence_recu.save()
            #semenceForm.save_m2m()
          
            messages.success(request, "Enregistrement effectué avec succès")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            #return HttpResponse("Enregistrement effectué avec succès")

        


    context = {
        'instance':instance,
        'semences':semences,
        'semenceForm':semenceForm,
        'total_plants_a_produire':total_plants_a_produire,
    }
    return render(request, 'cooperatives/detail_pepiniere.html', context)


@api_view(['POST'])
def edit_semence(request):
    id = request.POST['instance_id']
    instance = get_object_or_404(Semence_Pepiniere, id=id)
    form = SemenceForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            semence = form.save(commit=False)
            semence.save()
            return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": id},safe=False)
        else:
            return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)
        



def edit_semence_view(request):
    
    id = request.GET['id']
    instance = get_object_or_404(Semence_Pepiniere, id=id)
    form = SemenceForm(request.POST or None, request.FILES or None, instance=instance)
 

    context = {
        "instance": instance,
        "semenceForm": form,
    }
    
    templateStr = render_to_string("cooperatives/edit_semence.html", context)
    return JsonResponse({'templateStr':templateStr,'id':id},safe=False)

def delete_semence(request,id=None):
    semence = get_object_or_404(Semence_Pepiniere, id=id)
    semence.delete()

@api_view(['GET'])
def semence_by_pepiniere(request,id=None):
    instance = get_object_or_404(Pepiniere, id=id)
    semences = Semence_Pepiniere.objects.all().filter(pepiniere_id=instance)
    total_plants_a_produire = Semence_Pepiniere.objects.all().filter(pepiniere_id=instance).aggregate(total=Sum('production'))['total']

    context = {
        "semences": semences,
        "instance": instance,
        "t_semence": total_plants_a_produire
    }
    
    templateStr = render_to_string("cooperatives/tab_semences.html", context)
    return JsonResponse({'templateStr':templateStr,'id':id},safe=False)
