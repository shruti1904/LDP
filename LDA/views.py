from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Transformer, Building, Connection, User
from django.urls import reverse
import googlemaps
from .gmapsDistMatrix.distance_matrix import distance_matrix
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core import serializers

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

def add_connections(request): # Not mapped to a url yet.
    gmaps = googlemaps.Client(key='AIzaSyD-IxdRdp56dYFVy-06EMG9VD1RCSwUWdk')
    # Backup key - AIzaSyDfWidKLPWeb8ajWtI9W9ATSCaFJFPfV9w

    # Add all virtual connections
    for t in Transformer.objects.all():
        for b in Building.objects.all():
            if (Connection.objects.filter(Transformer = t, Building = b).exists() == False):
                origin = (t.Latitude, t.Longitude)
                destination = (b.Latitude, b.Longitude)
                mat = distance_matrix(gmaps, origin, destination)
                newC = Connection(Transformer = t, Building = b, Distance = mat['rows'][0]['elements'][0]['distance']['value'], Connected = False)
                newC.save()
                print(newC)

    # Update Connected to True for the buildings and transformers which are actually connected
    for b in Building.objects.all():
        t = Transformer.objects.get(id = b.Transformer_id)
        if Connection.objects.filter(Transformer = t, Building = b, Connected = False).exists():
            c = Connection.objects.get(Transformer = t, Building = b, Connected = False)
            c.Connected = True
            c.save()
            t.Load += b.ConnectedLoad
            t.save()

    return HttpResponseRedirect(reverse('LDA:graph'))

def toggle(request):
    tID = request.POST["t_ID"]
    oldT = get_object_or_404(Transformer, id = tID)
    if oldT.Status == True:
        # Shut the transformer down, set its load to 0 and save it to the database
        oldT.Status = False
        oldT.Load = 0
        oldT.save()
        for conn in oldT.connection_set.filter(Connected = True):
            # Disconnect the buildings which are connected to the transformer.
            conn.Connected = False
            conn.save()
            b = conn.Building
            feasibilities = {}
            for newT in Transformer.objects.filter(Status = True):
                dist = Connection.objects.get(Transformer = newT, Building = b).Distance
                feasibility = ((0.8 * newT.kVA) -  newT.Load) / dist
                feasibilities[newT.id] = feasibility
            if max(feasibilities.values()) > 0:
                newTransID = max(feasibilities, key = feasibilities.get)
                switchTo = Transformer.objects.get(id = newTransID)
                Connection.objects.filter(Transformer = switchTo, Building = b).update(Connected = True)
                switchTo.Load += b.ConnectedLoad
                switchTo.save()
    else:
        oldT.Status = True
        for b in oldT.building_set.all():
            oldT.Load += b.ConnectedLoad
            if (Connection.objects.filter(Building = b, Connected = True).exists()):
                c = Connection.objects.get(Building = b, Connected = True)
                c.Connected = False
                c.Transformer.Load -= b.ConnectedLoad
                c.Transformer.save()
                c.save()
            Connection.objects.filter(Transformer = oldT, Building = b).update(Connected = True)
        oldT.save()
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
