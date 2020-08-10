# Generated by Django 3.0.7 on 2020-06-27 17:46

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activityName', models.CharField(default='Computers', max_length=30)),
                ('activityType', models.CharField(choices=[('CO_CURR', 'Co Curricular'), ('EXTRA_CURR', 'Extra Curricular')], default='CO_CURR', max_length=25)),
            ],
            options={
                'verbose_name_plural': 'Acitivities',
            },
        ),
        migrations.CreateModel(
            name='Camp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curLevel', models.IntegerField(default=1)),
                ('campDay', models.IntegerField(default=1)),
                ('startDate', models.DateField(blank=True, default=datetime.datetime(2020, 6, 27, 17, 46, 34, 563328, tzinfo=utc), null=True)),
                ('nextCampDate', models.DateField(blank=True, default=datetime.datetime(2020, 6, 27, 17, 46, 34, 563360, tzinfo=utc), null=True)),
                ('status', models.CharField(choices=[('UPCOMING', 'Upcoming'), ('ONGOING', 'Ongoing'), ('COMPLETED', 'Completed')], default='UPCOMING', max_length=15)),
                ('scheduleGenerated_By_CL', models.BooleanField(default=False)),
                ('batchesExist', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cityName', models.CharField(max_length=30)),
                ('stateName', models.CharField(max_length=30)),
                ('country', models.CharField(default='India', max_length=30)),
            ],
            options={
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='App_CampDiaries.Camp')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isFirstTime', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=50)),
                ('userRole', models.CharField(choices=[('VOLUNTEER', 'Volunteer'), ('ACTIVITY_LEAD', 'Activity Lead'), ('CAMP_LEAD', 'Camp Lead'), ('CITY_LEAD', 'City Lead'), ('ADMIN', 'Admin')], default='VOLUNTEER', max_length=20)),
                ('phoneNumber', models.CharField(max_length=13)),
                ('email', models.CharField(max_length=50)),
                ('campDays', models.IntegerField(default=0)),
                ('notifications', models.ManyToManyField(blank=True, null=True, related_name='users', to='App_CampDiaries.Notification')),
                ('readNotifications', models.ManyToManyField(blank=True, null=True, related_name='ready_by_users', to='App_CampDiaries.Notification')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schoolName', models.CharField(max_length=30)),
                ('addressLine', models.TextField()),
                ('pinCode', models.CharField(max_length=10)),
                ('totalStudentsCount', models.IntegerField(default=-1)),
                ('isSatPref', models.BooleanField(blank=True, default=True, null=True)),
                ('isSunPref', models.BooleanField(blank=True, default=True, null=True)),
                ('city', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='schools', to='App_CampDiaries.City')),
            ],
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActLead', models.BooleanField(default=False, null=True)),
                ('isSatPref', models.BooleanField(default=True, null=True)),
                ('isSunPref', models.BooleanField(default=True, null=True)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Activity')),
                ('camps', models.ManyToManyField(blank=True, null=True, related_name='volunteers', to='App_CampDiaries.Camp')),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='VolCampDayStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campDay', models.IntegerField(default=-1)),
                ('isGoing', models.BooleanField(default=False)),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Camp')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Volunteer')),
            ],
            options={
                'verbose_name_plural': 'Volunteer Camp Day Status',
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campDay', models.IntegerField(default=-1)),
                ('roomDetails', models.TextField(default=-1)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Activity')),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='venues', to='App_CampDiaries.Camp')),
            ],
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campDay', models.IntegerField(default=-1)),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='histories', to='App_CampDiaries.Camp')),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Profile')),
            ],
            options={
                'verbose_name_plural': 'User Histories',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rollNumber', models.IntegerField(default=0)),
                ('studentName', models.CharField(max_length=30)),
                ('standard', models.IntegerField(default=-1)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='App_CampDiaries.School')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dayOfWeek', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THUR', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], default='SAT', max_length=10)),
                ('campDay', models.IntegerField(default=1)),
                ('date', models.DateField()),
                ('startTime', models.TimeField(default=datetime.time(10, 0))),
                ('endTime', models.TimeField(default=datetime.time(14, 15))),
                ('session1StartTime', models.TimeField(default=datetime.time(10, 0))),
                ('session2StartTime', models.TimeField(default=datetime.time(11, 0))),
                ('session3StartTime', models.TimeField(default=datetime.time(13, 0))),
                ('session4StartTime', models.TimeField(default=datetime.time(14, 0))),
                ('breakStartTime', models.TimeField(default=datetime.time(12, 0))),
                ('breakEndTime', models.TimeField(default=datetime.time(13, 0))),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='App_CampDiaries.Camp')),
            ],
        ),
        migrations.CreateModel(
            name='Replacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campDay', models.IntegerField(default=-1)),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Camp')),
                ('replacement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replacementFor', to='App_CampDiaries.Profile')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Volunteer')),
            ],
        ),
        migrations.CreateModel(
            name='Relation_User_Camp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Camp')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeStamp', models.DateTimeField()),
                ('message', models.TextField()),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='camp_to_messages', to='App_CampDiaries.Camp')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_to_messages', to='App_CampDiaries.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Level3Pref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coCurrPref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level3_coCurrPrefs', to='App_CampDiaries.Activity')),
                ('extraCurrPref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level3_extraCurrPrefs', to='App_CampDiaries.Activity')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Level2Pref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coCurrPref1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level2_coCurrPrefs1', to='App_CampDiaries.Activity')),
                ('coCurrPref2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level2_coCurrPrefs2', to='App_CampDiaries.Activity')),
                ('extraCurrPref1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level2_extraCurrPrefs1', to='App_CampDiaries.Activity')),
                ('extraCurrPref2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level2_extraCurrPrefs2', to='App_CampDiaries.Activity')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Student')),
            ],
        ),
        migrations.CreateModel(
            name='CityLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city_leads', to='App_CampDiaries.City')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='CampLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camps', models.ManyToManyField(blank=True, null=True, related_name='camp_leads', to='App_CampDiaries.Camp')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='camp',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='camps', to='App_CampDiaries.City'),
        ),
        migrations.AddField(
            model_name='camp',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App_CampDiaries.School'),
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campDay', models.IntegerField(default=-1)),
                ('batchNum', models.IntegerField(default=-1)),
                ('activity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activityBatches', to='App_CampDiaries.Activity')),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campBatches', to='App_CampDiaries.Camp')),
                ('students', models.ManyToManyField(to='App_CampDiaries.Student')),
            ],
            options={
                'verbose_name_plural': 'Batches',
            },
        ),
    ]