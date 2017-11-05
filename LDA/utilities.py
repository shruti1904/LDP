from django.shortcuts import get_object_or_404
from .models import Transformer, Building, Connection, LoadLog
from django.utils import timezone
import googlemaps
from .gmapsDistMatrix.distance_matrix import distance_matrix

def toggle(tID):
    oldT = get_object_or_404(Transformer, id = tID)
    ChangedBuildings = []
    if oldT.Status == True:
        # Shut the transformer down, set its load to 0 and save it to the database
        oldT.Status = False
        oldT.Load = 0
        oldT.save()
        LoadLog(Transformer = oldT, Load = oldT.Load, Time = timezone.now()).save()
        for conn in oldT.connection_set.filter(Connected = True):
            # Disconnect the buildings which are connected to the transformer.
            conn.Connected = False
            conn.save()
            b = conn.Building
            feasibilities = {}
            for newT in Transformer.objects.filter(Status = True):
                dist = Connection.objects.get(Transformer = newT, Building = b).Distance
                feasibility = ((0.8 * newT.kVA) -  newT.Load - b.ConnectedLoad) / dist
                feasibilities[newT.id] = feasibility
            if max(feasibilities.values()) > 0:
                newTransID = max(feasibilities, key = feasibilities.get)
                switchTo = Transformer.objects.get(id = newTransID)
                Connection.objects.filter(Transformer = switchTo, Building = b).update(Connected = True)
                switchTo.Load += b.ConnectedLoad
                switchTo.save()
                ChangedBuildings.append(b.id)
                LoadLog(Transformer = switchTo, Load = switchTo.Load, Time = timezone.now()).save()
    else:
        oldT.Status = True
        for b in oldT.building_set.all():
            oldT.Load += b.ConnectedLoad
            if (Connection.objects.filter(Building = b, Connected = True).exists()):
                c = Connection.objects.get(Building = b, Connected = True)
                c.Connected = False
                c.Transformer.Load -= b.ConnectedLoad
                c.Transformer.save()
                LoadLog(Transformer = c.Transformer, Load = c.Transformer.Load, Time = timezone.now()).save()
                c.save()
            ChangedBuildings.append(b.id)
            Connection.objects.filter(Transformer = oldT, Building = b).update(Connected = True)
        oldT.save()
        LoadLog(Transformer = oldT, Load = oldT.Load, Time = timezone.now()).save()

    return ChangedBuildings

def add_connections():
    gmaps = googlemaps.Client(key='AIzaSyD-IxdRdp56dYFVy-06EMG9VD1RCSwUWdk')
    # Backup key - AIzaSyDfWidKLPWeb8ajWtI9W9ATSCaFJFPfV9w

    # Add all virtual connections
    for t in Transformer.objects.all():
        for b in Building.objects.all():
            if (Connection.objects.filter(Transformer = t, Building = b).exists() == False):
                origin = (t.Latitude, t.Longitude)
                destination = (b.Latitude, b.Longitude)
                mat = distance_matrix(gmaps, origin, destination)
                distance = mat['rows'][0]['elements'][0]['distance']['value']
                if (distance == 0):
                    distance = 1
                newC = Connection(Transformer = t, Building = b, Distance = distance, Connected = False)
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
            LoadLog(Transformer = t, Load = t.Load, Time = timezone.now()).save()
