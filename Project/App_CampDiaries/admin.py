from django.contrib import admin
from .models import *

models_arr = [City, Activity, Camp, Schedule, Venue, School, Notification, Profile, Relation_User_Camp, UserHistory, Message, Student, Batch,  Volunteer, CampLead, CityLead, VolCampDayStatus, Replacement, Level2Pref, Level3Pref]
admin.site.register(models_arr)