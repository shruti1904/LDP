from django.db import models

# Create your models here.

class Transformer(models.Model):
	Name = models.CharField(max_length = 50)
	Manufacturer = models.CharField(max_length = 50)
	kVA = models.FloatField()
	NoLoadVoltage_HV = models.IntegerField()
	NoLoadVoltage_LV = models.IntegerField()
	Current_HV = models.FloatField()
	Current_LV = models.FloatField()
	Phase_HV = models.IntegerField()
	Phase_LV = models.IntegerField()
	Frequency = models.IntegerField()
	Type = models.CharField(max_length = 10)
	ImpedanceVolt = models.FloatField()
	Latitude = models.DecimalField(max_digits = 10, decimal_places = 6)
	Longitude = models.DecimalField(max_digits = 10, decimal_places = 6)
	Load = models.FloatField()
	Status = models.BooleanField(default = True) # True = ON. False = OFF.

	def __str__(self):
		return self.Name

	def dict(self):
		transformerDict = {}
		transformerDict['id'] = self.id
		transformerDict['label'] = self.Name
		transformerDict['font'] =	{'color':'white'}

		if( self.Status == True):
			if( self.Load <= self.kVA):
				transformerDict['color'] = '#047a00'
			else:
				transformerDict['color'] = '#e21d1d'		
		else:
			transformerDict['color'] = '#777'
		return transformerDict
	
	def getId(self):
		return self.id

class Building(models.Model):
	Name = models.CharField(max_length = 50)
	Transformer = models.ForeignKey(Transformer, on_delete = models.CASCADE)
	ConnectedLoad = models.FloatField() # Load in kVA
	MaximumDemand = models.FloatField() # MD in kVA
	Latitude = models.DecimalField(max_digits = 10, decimal_places = 6)
	Longitude = models.DecimalField(max_digits = 10, decimal_places = 6)

	def __str__(self):
		return self.Name

	def dict(self):
		buildingDict = {'id' : self.id + Transformer.objects.all().count(), 
						'label' : self.Name, 
						'shape': 'dot', 
						'size': 10, 
						'color' : '#29568F'};
		return buildingDict

class Connection(models.Model):
	Transformer = models.ForeignKey(Transformer, on_delete = models.CASCADE)
	Building = models.ForeignKey(Building, on_delete = models.CASCADE) 
	Distance = models.IntegerField(default = 0)
	Connected = models.BooleanField(default = False)

	def __str__(self):
		return str(self.Transformer) + " -> " + str(self.Building)

	def dict(self):
		return {
			'from': self.Transformer.id,
			'to': self.Building.id+ Transformer.objects.all().count(),
			'color': {
				'color':'black'
			}
		}

class User(models.Model):
	FullName = models.CharField(max_length=50)
	Email = models.CharField(max_length=20)
	Password = models.CharField(max_length=20)

	def __str__(self):
		return str(self.FullName)

class LoadLog(models.Model):
    Transformer = models.ForeignKey(Transformer, on_delete = models.CASCADE)
    Load = models.FloatField()
    Time = models.DateTimeField()
