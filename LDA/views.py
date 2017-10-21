from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Transformer, Building, Connection, User, LoadLog
from django.urls import reverse
import googlemaps
from .gmapsDistMatrix.distance_matrix import distance_matrix
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core import serializers
from . import utilities
# Create your views here.
def index(request):
    return render(request, 'LDA/index.html', {})

def graph(request):
    if('user' not in request.session):
        return redirect("http://localhost/wordpress/")

    transformers_list = Transformer.objects.all()
    buildings_list = Building.objects.all()
    connection_list = Connection.objects.filter(Connected = True)

    context = {
        'trans_list' : transformers_list,
        'buil_list' : buildings_list,
        'conn_list' : connection_list,
    }
    return render(request, 'LDA/graph.html', context)

def add_connections(request):
    utilities.add_connections()
    return HttpResponseRedirect(reverse('LDA:graph'))

def toggle(request):
    tID = request.POST["t_ID"]
    utilities.toggle(tID)
    return HttpResponseRedirect(reverse('LDA:graph'))


@csrf_exempt
def signup(request):
    name = request.POST["fullName"]
    email = request.POST["email"]
    password = request.POST["password"]
    u = User(FullName = name, Email = email, Password = password)
    u.save()
    request.session['user'] = email

    if(User.objects.filter(Email = email, Password = password).exists()):
        return HttpResponseRedirect(reverse('LDA:graph'))
    else:
        return HttpResponse("Something Went Wrong with the Sign Up process")

@csrf_exempt
def login(request):
    email = request.POST["email"]
    password = request.POST["password"]
    request.session['user'] = email
    if(User.objects.filter(Email = email, Password = password).exists()):
        return HttpResponseRedirect(reverse('LDA:graph'))
    else:
        return HttpResponse("Wrong email or password")

@csrf_exempt
def logout(request):
    del request.session['user']
    return redirect("http://localhost/wordpress/")

@csrf_exempt
def getTransformer(request):
    t = Transformer.objects.filter(id=request.POST["id"])
    return JsonResponse(serializers.serialize('json',t),safe=False)

@csrf_exempt
def getBuilding(request):
    b = Building.objects.filter(id=request.POST["id"])
    return JsonResponse(serializers.serialize('json',b),safe=False)


@csrf_exempt
def LoadLogRequest(request):
    tID = request.POST["ID"]
    logs = LoadLog.objects.filter(Transformer = tID)
    jsonLog = []
    for l in logs:
        dict = {}
        key = str(l.Time)
        dict['time'] = key
        dict['load'] = l.Load
        jsonLog.append(dict)
    return JsonResponse(jsonLog,safe=False)


@csrf_exempt
def getConnectedBuildings(request):
    c = Connection.objects.filter(Transformer=request.POST["id"],Connected=True)
    NumberList = []
    for i in c:
        NumberList.append(i.Building)
    Data = []
    for i in NumberList:
        dict = []
        dict.append(i.Name)
        dict.append(i.ConnectedLoad)
        Data.append(dict)
    return JsonResponse(Data,safe=False)

@csrf_exempt
def getFeasibilityList(request):

    CONNECTIONS_LIST = Connection.objects.filter(Building=request.POST['id'])
    FeasibilityList = []
    for i, c in enumerate(CONNECTIONS_LIST):
        feasibility=0
        if c.Distance == 0:
            feasibility = 0
        elif(c.Connected):
            feasibility = ((0.8 * c.Transformer.kVA) -  c.Transformer.Load - c.Building.ConnectedLoad) / c.Distance
        else:
            feasibility = ((0.8 * c.Transformer.kVA) -  c.Transformer.Load) / c.Distance
        dict=[]
        dict.append(c.Transformer.Name)
        dict.append (feasibility)
        FeasibilityList.append(dict)
    return JsonResponse(FeasibilityList,safe=False)
