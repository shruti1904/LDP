# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-08 07:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=50)),
                ('ConnectedLoad', models.FloatField()),
                ('MaximumDemand', models.FloatField()),
                ('Latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('Longitude', models.DecimalField(decimal_places=6, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.IntegerField(default=0)),
                ('connected', models.BooleanField(default=False)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LDA.Building')),
            ],
        ),
        migrations.CreateModel(
            name='Transformer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=50)),
                ('Manufacturer', models.CharField(max_length=50)),
                ('kVA', models.FloatField()),
                ('NoLoadVoltage_HV', models.IntegerField()),
                ('NoLoadVoltage_LV', models.IntegerField()),
                ('Current_HV', models.FloatField()),
                ('Current_LV', models.FloatField()),
                ('Phase_HV', models.IntegerField()),
                ('Phase_LV', models.IntegerField()),
                ('Frequency', models.IntegerField()),
                ('Type', models.CharField(max_length=10)),
                ('ImpedanceVolt', models.FloatField()),
                ('Latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('Longitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('Load', models.FloatField()),
                ('Status', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='connection',
            name='transformer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LDA.Transformer'),
        ),
        migrations.AddField(
            model_name='building',
            name='Transformer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LDA.Transformer'),
        ),
    ]