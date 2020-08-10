from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import datetime


class City(models.Model):
    cityName = models.CharField(max_length=30)
    stateName = models.CharField(max_length=30)
    country = models.CharField(max_length=30, default="India")
    '''One to many for Schools'''
    '''One to Many for City Leads'''

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.cityName


class Activity(models.Model):
    ACTIVITY_CHOICES = (("CO_CURR", "Co Curricular"),
                        ("EXTRA_CURR", "Extra Curricular"))
    activityName = models.CharField(max_length=30, default="Computers")
    activityType = models.CharField(max_length=25, choices=ACTIVITY_CHOICES, default="CO_CURR")
    '''One to many for Venues'''
    '''batches -> saved as Many To Many in 'Batch' '''
    '''One to many for Prefs in l 2,3'''

    class Meta:
        verbose_name_plural = "Acitivities"

    def __str__(self):
        return self.activityName


class School(models.Model):
    schoolName = models.CharField(max_length=30)
    addressLine = models.TextField()
    pinCode = models.CharField(max_length=10)
    totalStudentsCount = models.IntegerField(default=-1)
    isSatPref = models.BooleanField(null=True, blank=True, default=True)
    isSunPref = models.BooleanField(null=True, blank=True, default=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='schools', default=1)
    '''One to many for students'''

    def __str__(self):
        return self.schoolName


class Camp(models.Model):
    STATUS = (
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed')
    )
    curLevel = models.IntegerField(default=1)
    campDay = models.IntegerField(default=1)
    startDate = models.DateField(default=timezone.now(), null=True, blank=True)
    nextCampDate = models.DateField(default=timezone.now(), null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='camps', null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default='UPCOMING')
    scheduleGenerated_By_CL = models.BooleanField(default=False)
    batchesExist = models.BooleanField(default=False)
    '''schools-> saved as Many to Many in School'''
    '''One to many for Volunteer'''
    '''One to many for Camp Lead'''
    '''One to many for batches'''
    '''One to many for Schedule'''
    '''One to many for Venue'''
    '''One to many for message'''
    '''One to many for VolCampDayStatus'''
    '''One to many for userHistory'''
    '''One to many for notification'''

    def __str__(self):
        return "School: " + str(self.school)


class Schedule(models.Model):
    DAYS = (
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THUR", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday")
    )
    dayOfWeek = models.CharField(max_length=10, choices=DAYS, default="SAT")
    campDay = models.IntegerField(default=1)
    date = models.DateField()
    startTime = models.TimeField(default=datetime.time(10, 00))
    endTime = models.TimeField(default=datetime.time(14, 15))
    session1StartTime = models.TimeField(default=datetime.time(10, 00))
    session2StartTime = models.TimeField(default=datetime.time(11, 00))
    session3StartTime = models.TimeField(default=datetime.time(13, 00))
    session4StartTime = models.TimeField(default=datetime.time(14, 00))
    breakStartTime = models.TimeField(default=datetime.time(12, 00))
    breakEndTime = models.TimeField(default=datetime.time(13, 00))
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='schedules')
    '''One to many for students'''

    def __str__(self):
        return str(self.camp) + " Camp day: " + str(self.campDay)


class Venue(models.Model):
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name="venues")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    campDay = models.IntegerField(default=-1)
    roomDetails = models.TextField(default=-1)

    def __str__(self):
        return self.roomDetails


class Notification(models.Model):
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='notifications')
    '''users -> saved as Many To Many in 'Profile' '''

    def __str__(self):
        return self.content


class Profile(models.Model):
    ROLE_CHOICES = (
        ('VOLUNTEER', 'Volunteer'),
        ('ACTIVITY_LEAD', 'Activity Lead'),
        ('CAMP_LEAD', 'Camp Lead'),
        ('CITY_LEAD', 'City Lead'),
        ('ADMIN', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    isFirstTime = models.BooleanField(default=True)
    name = models.CharField(max_length=50)
    userRole = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VOLUNTEER')
    phoneNumber = models.CharField(max_length=13)
    email = models.CharField(max_length=50)
    campDays = models.IntegerField(default=0)
    readNotifications = models.ManyToManyField(Notification, related_name="ready_by_users", null=True, blank=True)
    notifications = models.ManyToManyField(Notification, related_name="users", null=True, blank=True)
    '''One to many for messages'''
    '''One to many for userHistory'''
    '''One to many for Volunteer'''
    '''One to many for Camp Lead'''
    '''One to many for City Lead'''

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)


class Relation_User_Camp(models.Model):
    profile = models.ForeignKey(Profile, null=False, on_delete=models.CASCADE)
    camp = models.ForeignKey(Camp, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.camp) + ", User: " + self.profile.name


class UserHistory(models.Model):
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='histories')
    campDay = models.IntegerField(default=-1)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "User Histories"

    def __str__(self):
        return str(self.camp) + ", User: " + self.profile.name


class Message(models.Model):
    timeStamp = models.DateTimeField()
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_to_messages')
    message = models.TextField()
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name="camp_to_messages")

    # messageStatus = models.ChartField(10)
    def __str__(self):
        return self.message + ", Sent by: " + self.sender.name


class Student(models.Model):
    rollNumber = models.IntegerField(default=0)
    studentName = models.CharField(max_length=30)
    standard = models.IntegerField(default=-1)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    '''batches -> saved as Many To Many in 'Batch' '''
    '''One to many for Preferences in level 2,3'''

    def __str__(self):
        return self.studentName


class Batch(models.Model):
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='campBatches')
    campDay = models.IntegerField(default=0)
    batchNum = models.IntegerField(default=-1)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="activityBatches", null=True)
    students = models.ManyToManyField(Student)

    class Meta:
        verbose_name_plural = "Batches"

    def __str__(self):
        return "Activity: " + str(self.activity) + ", Batch num: " + str(self.batchNum) + ", Camp day: " + str(self.campDay)


class Volunteer(models.Model):
    isActLead = models.BooleanField(null=True, default=False)
    isSatPref = models.BooleanField(null=True, default=True)
    isSunPref = models.BooleanField(null=True, default=True)
    camps = models.ManyToManyField(Camp, related_name='volunteers', null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    '''One to many for VolCampDayStatus'''

    def __str__(self):
        return self.profile.name


class CampLead(models.Model):
    camps = models.ManyToManyField(Camp, related_name='camp_leads', null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.name


class CityLead(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_leads')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.name


class VolCampDayStatus(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    campDay = models.IntegerField(default=-1)
    isGoing = models.BooleanField(default=False)
    '''One to Many for Replacement'''

    class Meta:
        verbose_name_plural = "Volunteer Camp Day Status"

    def __str__(self):
        return str(self.volunteer)


class Replacement(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    replacement = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="replacementFor")
    campDay = models.IntegerField(default=-1)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)

    def __str__(self):
        return "Volunteer: " + str(self.volunteer) + ", Replacement: " + self.replacement.name


class Level2Pref(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    coCurrPref1 = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="level2_coCurrPrefs1")
    coCurrPref2 = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="level2_coCurrPrefs2")
    extraCurrPref1 = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="level2_extraCurrPrefs1")
    extraCurrPref2 = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="level2_extraCurrPrefs2")

    def __str__(self):
        return "Student: " + str(self.student.studentName)


class Level3Pref(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    coCurrPref = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="level3_coCurrPrefs")
    extraCurrPref = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="level3_extraCurrPrefs")

    def __str__(self):
        return "Student: " + str(self.student.studentName)