from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import *


class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class ActivitySerializer(ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


class SchoolSerializer(ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = School
        exclude = ('isSatPref', 'isSunPref', 'id')


class CampSerializer(ModelSerializer):
    city = CitySerializer()
    school = SchoolSerializer()

    class Meta:
        model = Camp
        fields = "__all__"


class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        exclude = ('camp',)


class VenueSerializer(ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        exclude = ('camp', )


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'name', 'isFirstTime', 'phoneNumber', 'campDays', 'email', 'userRole')


class MessageSerializer(ModelSerializer):
    sender = ProfileSerializer()

    class Meta:
        model = Message
        fields = "__all__"


class UserHistorySerializer(ModelSerializer):
    class Meta:
        model = UserHistory
        fields = "__all__"


class StudentSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class BatchSerializer(ModelSerializer):
    students = StudentSerializer(many=True)

    class Meta:
        model = Batch
        exclude = ('camp', )


class VolunteerSerializer(ModelSerializer):
    profile = ProfileSerializer()
    activity = ActivitySerializer()

    class Meta:
        model = Volunteer
        fields = ('isActLead', 'profile', 'activity')


class CampLeadSerializer(ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = CampLead
        fields = ('profile',)


class CampInfoSerializer(ModelSerializer):
    volunteers = VolunteerSerializer(many=True)
    camp_leads = CampLeadSerializer(many=True)
    school = SchoolSerializer()

    class Meta:
        model = Camp
        exclude = ('startDate', 'nextCampDate', 'status', 'city')


class CityLeadSerializer(ModelSerializer):
    class Meta:
        model = CityLead
        fields = "__all__"


class VolCampDayStatusSerializer(ModelSerializer):
    class Meta:
        model = VolCampDayStatus
        fields = "__all__"


class ReplacementSerializer(ModelSerializer):
    class Meta:
        model = Replacement
        fields = "__all__"

class Level2PrefSerializer(ModelSerializer):
    coCurrPref1 = ActivitySerializer()
    coCurrPref2 = ActivitySerializer()
    extraCurrPref1 = ActivitySerializer()
    extraCurrPref2 = ActivitySerializer()
    student = StudentSerializer()
    class Meta:
        model = Level2Pref
        fields = "__all__"


class Level3PrefSerializer(ModelSerializer):
    coCurrPref = ActivitySerializer()
    extraCurrPref = ActivitySerializer()

    class Meta:
        model = Level3Pref
        fields = "__all__"
