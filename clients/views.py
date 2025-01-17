import os
from itertools import product
import datetime
import xlwt
from django.db.models import Count
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.staticfiles import finders
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.template.loader import get_template
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from twisted.words.protocols.jabber.jstrports import client
from xhtml2pdf import pisa

from .models import Client
from parametres.models import (
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    Activite,
    Region,
    Campagne, Cooperative
)

from cooperatives.models import (
    Producteur,
    Parcelle,
    Planting,
    Section,
    Sous_Section, Formation, Detail_Formation, DetailPlanting
)

def client_index(request):
    cooperatives = Cooperative.objects.all()
    AllCooperatives = Cooperative.objects.all()
    nb_cooperatives = Cooperative.objects.all().count()
    nb_producteurs = Producteur.objects.all().count()
    prod_coop = Cooperative.objects.annotate(nb_producteur=Count('producteurs'))
    #section_cooperative = Cooperative.objects.annotate(nb_section=Count('sections'))
    section_coop = Cooperative.objects.annotate(nb_section=Count('sections'))
    nb_parcelles = Parcelle.objects.all().count()
    Superficie = Parcelle.objects.aggregate(total=Sum('superficie'))['total']
    Total_plant = Planting.objects.aggregate(total=Sum('plant_recus'))['total']
    activate = "dashboard"

    context = {
        'cooperatives':cooperatives,
        'AllCooperatives':AllCooperatives,
        'nb_cooperatives': nb_cooperatives,
        'nb_producteurs': nb_producteurs,
        'nb_parcelles': nb_parcelles,
        'Superficie': Superficie,
        'Total_plant': Total_plant,
        'prod_coop': prod_coop,
        'section_coop': section_coop,
        'activate':activate
        #'section_cooperative': section_cooperative,
    }
    return render(request, 'clients/index.html', context)

def detail_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_nb_producteurs =
    section = Section.objects.filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.filter(section__cooperative_id=cooperative)
    # section_prod = Producteur.objects.all().filter(section_id__in=section).count()
    section_prod = Section.objects.annotate(nb_producteur=Count('producteurs'))    
    prod_section = Producteur.objects.filter(section_id__in=section).count()
    coop_nb_producteurs = Producteur.objects.filter(cooperative_id=cooperative).count()
    nb_formations = Formation.objects.filter(cooperative_id=cooperative).count()
    parcelles_section = Parcelle.objects.filter(producteur__section_id__in=section).count()
    # section_parcelle = Section.objects.annotate(nb_producteur=Count('producteurs.parcelles'))
    coop_nb_parcelles = Parcelle.objects.filter(producteur__section__cooperative_id=cooperative).count()
    coop_superficie = Parcelle.objects.filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    section_superf = Parcelle.objects.filter(producteur__section_id__in=section).aggregate(total=Sum('superficie'))['total']
    # section_plating = Planting.objects.filter(parcelle__producteur__section_id__in=section).aggregate(total=Sum('plant_recus'))['total']
    # plantings = DetailPlanting.objects.values("espece__libelle").filter(planting__parcelle__producteur__cooperative_id=cooperative).annotate(plante=Sum('plant_recus'))
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
        'section_prod': section_prod,
        # 'section_parcelle': section_parcelle,
        'parcelles_section': parcelles_section,
        'coop_plants_total': coop_plants_total,
        'section_superf': section_superf,        
        # 'labels': labels,
        # 'data': data,
    }
    return render(request, 'clients/Coop/cooperative.html', context)

def section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sections = Section.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sections': coop_sections,
    }
    return render(request, 'clients/Coop/coop_sections.html', context)

def sous_section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sous_sections': coop_sous_sections,
    }
    return render(request, 'clients/Coop/coop_sous_sections.html', context)

def prod_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    # coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_producteurs': coop_producteurs,
    }
    return render(request, 'clients/Coop/coop_producteurs.html', context)

def parcelle_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_parcelles' : coop_parcelles,
    }
    return render(request, 'clients/Coop/coop_parcelle.html', context)

def planting_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_plants = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_plants': coop_plants,
    }
    return render(request, 'clients/Coop/coop_plantings.html', context)

def projet(request):
    client = Client.objects.get(user_id=request.user.id)
    projets = Projet.objects.all().filter(client_id=client)
    context = {
        'client': client,
        'projets': projets,
    }
    return render(request, 'clients/projets.html', context)

def detail_proj(request, id=None):
    instance = get_object_or_404(Projet, id=id)
    # cooperatives = Cooperative.objects.filter(cooperative__projet__i).count()
    producteurs_proj = Producteur.objects.filter(cooperative__projet=instance).count()
    parcelles = Parcelle.objects.filter(producteur__cooperative__projet=instance)
    # parcelles = Planting.objects.all().filter(projet_id=instance)
    nb_parcelles_proj = Parcelle.objects.filter(producteur__cooperative__projet=instance).count()
    plants = DetailPlanting.objects.filter(planting__projet_id=instance).aggregate(total=Sum('nb_plante'))['total']
    #nb_plants_proj = Planting.objects.all().filter(projet_id = instance).count()
    superficie_proj = Parcelle.objects.filter(producteur__cooperative__projet=instance).aggregate(total=Sum('superficie'))['total']

    # print(superficie_proj)
    context = {
        'instance': instance,
        'parcelles': parcelles,
        # 'cooperatives': cooperatives,
        'plants':plants,
        # 'parcelles':plants,
        'nb_parcelles_proj':nb_parcelles_proj,
        #'nb_plants_proj':nb_plants_proj,
        #'plants':plants,
        'superficie_proj':superficie_proj,
        'producteurs_proj':producteurs_proj,
    }
    return render(request, 'clients/projet.html', context)

def formations(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_formations = Formation.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_formations': coop_formations,
    }
    return render(request, 'clients/Coop/coop_formations.html', context)

def detail_formation(request, id=None, _id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    instance = get_object_or_404(Formation, id=_id)
    # instance = Formation.objects.all().filter(cooperative_id=cooperative)
    participants = Detail_Formation.objects.all().filter(formation_id=instance)
    # participants = Producteur.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative':cooperative,
        'instance':instance,
        'participants':participants,
        # 'detailFormation':detailFormation,
        # 'participants': participants,
    }
    return render(request, 'clients/Coop/detail_formation1.html', context)

def localisation(request):
    parcelles = Parcelle.objects.all()
    context = {
        'parcelles' : parcelles
    }
    return render(request, 'clients/carte.html', context)

def localisation_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    points_coop = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'points_coop' : points_coop
    }
    return render(request, 'carte1.html', context)


#EXPORT EXCEL
@login_required(login_url='connexion')
def export_prod_xls(request, id=None):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['COOPERATIVE', 'CODE', 'NOM ET PRENOMS', 'SECTION', 'LOCALITE', 'STATUT']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = get_object_or_404(Cooperative, id=id)
    rows = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'cooperative__sigle',
        'code',
        'nom',
        'section__libelle',
        'localite',
        'type_producteur',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

@login_required(login_url='connexion')
def export_parcelle_xls(request, id=None):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Parcelles.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Parcelles')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['COOPERATIVE', 'CODE', 'PRODUCTEUR', 'SECTION', 'LOCALITE', 'SUPER', 'LAT', 'LONG']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = get_object_or_404(Cooperative, id=id)
    rows = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative.id).values_list(
        'producteur__cooperative__sigle',
        'code',
        'producteur__nom',
        'producteur__section__libelle',
        'producteur__localite',
        'superficie',
        'latitude',
        'longitude',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#EXPORT PDF
def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
@login_required(login_url='connexion')
def export_prods_to_pdf(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    template_path = 'cooperatives/producteurs_pdf.html'
    context = {
        'cooperative' : cooperative,
        'producteurs': producteurs,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste Producteur.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response

@login_required(login_url='connexion')
def export_parcelles_to_pdf(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    template_path = 'cooperatives/new_parcelles_pdf.html'
    context = {
        'cooperative': cooperative,
        'parcelles': parcelles,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste Producteur.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response

#Statistiques Charts
def producteur_section(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    section = Section.objects.filter(cooperative_id=cooperative)
    querysets = Producteur.objects.filter(section_id__in=section).values("section__libelle")
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['section__libelle'])
        data.append(stat['qte_recu'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

def Plantings(request):
    querysets = Planting.objects.values("parcelle__producteur__cooperative__sigle").annotate(plant_recus=Sum('plant_recus'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['parcelle__producteur__cooperative__sigle'])
        data.append(stat['plant_recus'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

def DetailPlantings(request):
    querysets = DetailPlanting.objects.values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data= {
        'labels':labels,
        'data':data,
    })


def coopdetailPlantings(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    querysets = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data= {
        'labels':labels,
        'data':data,
    })

def plants_par_section(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    sections = Section.objects.filter(cooperative_id = cooperative)
    querysets = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).filter(planting__parcelle__producteur__section_id__in=sections).values("planting__parcelle__producteur__section__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['planting__parcelle__producteur__section__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data= {
        'labels':labels,
        'data':data,
    })



# Create your views here.
