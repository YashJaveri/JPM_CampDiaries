from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class ProfileApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user:
            profile = request.user.profile
            serializer = ProfileSerializer(profile)

            isFirstTime = 0
            if profile.isFirstTime:
                isFirstTime = 1  # First time login

            content = {"isFirstTime": isFirstTime, "profile": serializer.data}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'message': 'Auth failed'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)


class ChangePassword(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # Incorrect json format
        if 'oldPassword' not in request.data.keys() or 'newPassword' not in request.data.keys():
            return Response({'message': 'Incorrect JSON input'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user is not None:
            user = authenticate(username=request.user.username, password=request.data["oldPassword"])
            # Incorrect match
            if user is None:
                return Response({'message': 'Old password is incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)

            # Correct match
            request.user.set_password(request.data['newPassword'])
            request.user.save()
            profile = request.user.profile
            if profile.isFirstTime:
                profile.isFirstTime = False  # Once password is changed, it is no more first time login
                profile.save()
            return Response({'message': 'Successfully changed'}, status=status.HTTP_205_RESET_CONTENT)

        # User not found/Unauthorized
        return Response({'message': 'Username or password incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)


def categorizingCamps(camps):
    categorizedCamps = {"UPCOMING": [], "ONGOING": [], "COMPLETED": []}
    # sort by category
    for camp in camps:
        serializedCamp = CampSerializer(camp).data
        if camp.status == 'UPCOMING':
            categorizedCamps['UPCOMING'].append(serializedCamp)
        if camp.status == 'ONGOING':
            categorizedCamps['ONGOING'].append(serializedCamp)
        if camp.status == 'COMPLETED':
            categorizedCamps['COMPLETED'].append(serializedCamp)
    return categorizedCamps


class CampByCityApiView(APIView):
    def get(self, request, passedCityId):
        # Public request
        if str(request.user) is "AnonymousUser":
            camps = Camp.objects.filter(city=passedCityId)
            categorizedCamps = categorizingCamps(camps)
            return Response(categorizedCamps, status=status.HTTP_200_OK)

        else:
            if request.user:
                profile = request.user.profile
                if (passedCityId is not None) and (profile.userRole != "ADMIN"):
                    return Response({'message': 'You cant access camps outside your city'},
                                    status=status.HTTP_401_UNAUTHORIZED)
                if passedCityId is not None and (profile.userRole == 'ADMIN'):
                    camps = Camp.objects.filter(city=passedCityId)
                    categorizedCamps = categorizingCamps(camps)
                    return Response(categorizedCamps, status=status.HTTP_200_OK)


class CampsApiView(APIView):
    def get(self, request):
        # Public request
        if str(request.user) is "AnonymousUser":
            camps = Camp.objects.all()
            categorizedCamps = categorizingCamps(camps)
            return Response(categorizedCamps, status=status.HTTP_200_OK)

        # Not public
        else:
            if request.user:
                profile = request.user.profile

                if profile.userRole == 'ADMIN':
                    camps = Camp.objects.all()

                elif profile.userRole == 'CITY_LEAD':
                    cityLead = get_object_or_404(CityLead, profile=profile.id)
                    camps = Camp.objects.filter(city=cityLead.city.id)

                elif profile.userRole == 'CAMP_LEAD':
                    campLead = get_object_or_404(CampLead, profile=profile.id)
                    camps = campLead.camps.all()

                elif profile.userRole == 'ACTIVITY_LEAD' or profile.userRole == 'VOLUNTEER':
                    volunteer = get_object_or_404(Volunteer, profile=profile.id)
                    camps = volunteer.camps.all()

                categorizedCamps = categorizingCamps(camps)
                return Response(categorizedCamps, status=status.HTTP_200_OK)
            else:
                # If totally Unauthorized
                return Response({'message': 'Username or password incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)


class CampInfoApiView(APIView):
    def get(self, request, campId):
        if str(request.user) == "AnonymousUser":
            camp = Camp.objects.get(pk=campId)
            serializer = CampInfoSerializer(camp)
            modifiedJson = {}
            modifiedJson.update(serializer.data)
            modifiedJson.pop('volunteers')
            allSchedules = Schedule.objects.filter(camp=campId)
            m_dict = {}
            for s in allSchedules:
                m_string = "day" + str(s.campDay)
                m_dict[m_string] = s.date
            modifiedJson["dates"] = m_dict
            return Response(modifiedJson, status=status.HTTP_200_OK)

        else:
            if request.user and str(request.user) != "AnonymousUser":
                campObj = Camp.objects.get(pk=campId)
                serializer = CampInfoSerializer(campObj)
                modifiedJson = {}
                modifiedJson.update(serializer.data)
                # Add dates
                allSchedules = Schedule.objects.filter(camp=campId)
                m_dict = {}
                for s in allSchedules:
                    m_string = "day" + str(s.campDay)
                    m_dict[m_string] = s.date
                modifiedJson["dates"] = m_dict
                day1, day2 = ((campObj.curLevel * 2) - 1), (campObj.curLevel * 2)
                # Schedules
                modifiedJson["schedules"] = []
                allSchedules = Schedule.objects.filter(camp=campId)
                for s in allSchedules:
                    if s.campDay == day1 or s.campDay == day2:
                        modifiedJson["schedules"].append(ScheduleSerializer(s).data)

                if campObj.scheduleGenerated_By_CL:  # Return schedule, batches as well
                    if day1 >= 5: day1 = 5;
                    if day2 >= 6: day1 = 6;
                    # Batches
                    modifiedJson["batches"] = []
                    campBatches = Batch.objects.filter(camp=campId)
                    for act in Activity.objects.all():
                        actDict = {}
                        actDict[act.activityName] = []
                        for b in campBatches:
                            if b.activity == act and (b.campDay == day1 or b.campDay == day2):
                                actDict[act.activityName].append(BatchSerializer(b).data)
                        modifiedJson["batches"].append(actDict)

                return Response(modifiedJson, status=status.HTTP_200_OK)
            elif request.user is None:
                return Response({'message': 'Username or password incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)


class CityApiView(APIView):
    def get(self, request):
        # Public request
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserExistsApiView(APIView):
    def get(self, request, email):
        profile = Profile.objects.all().filter(email=email)
        if profile:
            return Response({'message': 'User already exists'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)


class PublishScheduleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, campId):
        try:
            camp = Camp.objects.get(pk=campId)
            if camp.scheduleGenerated_By_CL:
                return Response({"message": "Schedule  already published for the given camp"},
                                status=status.HTTP_200_OK)
            else:
                camp.batchesExist = True
                camp.scheduleGenerated_By_CL = True
                camp.save()
                return Response({"message": "Successfully updated the flag"}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Camp not found"}, status=status.HTTP_404_NOT_FOUND)


class UpdateLevelApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        print(Camp.objects.values_list('id', flat=True))
        profile = request.user.profile
        if profile.userRole == "CAMP_LEAD":
            camp = Camp.objects.get(pk=request.data["campId"])
            content = "Successful"
            if camp.curLevel != request.data["level"]:  # Level updated
                content = checkForPrefsTaken(camp)
                if content == "Successful":
                    # Delete batches
                    if request.data["level"] <= 3:
                        camp.scheduleGenerated_By_CL = False
                        camp.batchesExist = False
                        Batch.objects.filter(camp=request.data["campId"]).delete()
                    camp.curLevel = request.data["level"]

            if content == "Successful":  # Students' prefs taken or level not yet updated
                camp.campDay = ((request.data["level"] * 2) - 1) if (request.data["campDay"] == 1) else (
                        request.data["level"] * 2)

                if camp.curLevel == 6 and camp.CampDay == 12:  # Camp completed
                    camp.status = "COMPLETED"
                else:
                    camp.status = "ONGOING"

                for schedule in camp.schedules.all():
                    if schedule.campDay == camp.campDay:
                        camp.nextCampDate = schedule.date
                        break

                camp.save()
                return Response({"message": "Successfully updated level"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "All students have not given their preferences", "notFound": content},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message': 'Only Camp Leads have permission to update camp levels/camp-days'},
                            status=status.HTTP_401_UNAUTHORIZED)


def checkForPrefsTaken(camp):
    students = camp.school.students.all()
    if camp.curLevel == 1:
        notFound = []
        for student in students:
            try:
                Level2Pref.objects.get(student=student)
            except:
                notFound.append(student)
    elif camp.curLevel >= 2:
        notFound = []
        for student in students:
            try:
                Level3Pref.objects.get(student=student)
            except:
                notFound.append(student)
    if len(notFound) == 0:
        return "Successful"
    else:
        return StudentSerializer(notFound, many=True).data


class GenerateBatchesApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        camp = Camp.objects.get(pk=request.data["campId"])
        print(Student.objects.values_list('id', flat=True))
        if profile.userRole == "CAMP_LEAD":  # Camp lead
            if camp.batchesExist is False:  # Batch do not exist
                if len(request.data["day1"]) == 0:  # And also, did not receive data
                    return Response({"message": "Batches do not exist, please send the data"},
                                    status=status.HTTP_409_CONFLICT)
                else:  # Batch generation:
                    if int(request.data["level"]) == 1:
                        message = self.generateBatches(request.data["day1"], camp, 1)
                        if message != "Successful":
                            return Response({"message": message}, status=status.HTTP_404_NOT_FOUND)

                        message = self.generateBatches(request.data["day2"], camp, 2)
                        if message != "Successful":
                            return Response({"message": message}, status=status.HTTP_404_NOT_FOUND)
                        else:
                            camp.batchesExist = True
                            camp.save()
                            content = self.campInfo(request.data["campId"], int(request.data["level"]))
                            return Response(content, status=status.HTTP_200_OK)

                    else:
                        message = self.generateBatches(request.data["day1"], camp,
                                                       (2 * int(request.data["level"]) - 1))
                        if message != "Successful":
                            return Response({"message": message}, status=status.HTTP_404_NOT_FOUND)
                        else:
                            camp.batchesExist = True
                            camp.save()
                            content = self.campInfo(request.data["campId"], int(request.data["level"]))
                            return Response(content, status=status.HTTP_200_OK)
            else:  # Batch exists, returning campInfo
                content = self.campInfo(request.data["campId"], int(request.data["level"]))
                return Response(content, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Only camp leads have permission to generate batches'},
                            status=status.HTTP_401_UNAUTHORIZED)

    def generateBatches(self, data, camp, campDay):
        for obj in data:
            actId = obj['actId']
            try:  # Check if activity exists
                activity = Activity.objects.get(pk=actId)
            except:
                return "Activity " + str(actId) + " does not exist."

            batches = obj['batches']
            batchObjs = []
            for batch in batches:
                batchNum = batch['batchNum']
                if Batch.objects.filter(camp=camp, campDay=campDay, batchNum=batchNum, activity=activity).count() == 0:
                    batchObj = Batch(camp=camp, campDay=campDay, batchNum=batchNum, activity=activity)
                    batchObjs.append(batchObj)
                    # batchObj.save()

            Batch.objects.bulk_create(batchObjs)

            for batchObj in batches:
                batchNum = batchObj['batchNum']
                batch = Batch.objects.get(camp=camp, campDay=campDay, batchNum=batchNum, activity=activity)
                studentIds = batchObj['students']
                for stId in studentIds:
                    try:  # Check if student exists
                        student = Student.objects.get(pk=stId)
                        if student not in batch.students.all():
                            batch.students.add(student)
                    except:
                        return "Student " + str(stId) + " does not exist."

        return "Successful"

    def campInfo(self, campId, level):
        campObj = Camp.objects.get(pk=campId)
        serializer = CampInfoSerializer(campObj)
        modifiedJson = {}
        modifiedJson.update(serializer.data)
        # Add dates
        allSchedules = Schedule.objects.filter(camp=campId)
        m_dict = {}
        for s in allSchedules:
            m_string = "day" + str(s.campDay)
            m_dict[m_string] = s.date
        modifiedJson["dates"] = m_dict
        day1, day2 = ((level * 2) - 1), (level * 2)
        # Schedules
        modifiedJson["schedules"] = []
        allSchedules = Schedule.objects.filter(camp=campId)
        for s in allSchedules:
            if s.campDay == day1 or s.campDay == day2:
                modifiedJson["schedules"].append(ScheduleSerializer(s).data)

        # Batches
        modifiedJson["batches"] = []
        campBatches = Batch.objects.filter(camp=campId)
        for act in Activity.objects.all():
            actDict = {}
            actDict[act.activityName] = []
            for b in campBatches:
                if b.activity == act and (b.campDay == day1 or b.campDay == day2):
                    actDict[act.activityName].append(BatchSerializer(b).data)
            modifiedJson["batches"].append(actDict)

        return modifiedJson


class CreateCampApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        if profile.userRole == "CITY_LEAD":
            schoolDict = request.data['school']
            volunteersDict = request.data['volunteers']
            studentsDict = request.data['students']
            camp_leadsDict = request.data['camp_leads']

            # Create School
            school = self.createSchool(schoolDict, studentsDict, profile)
            # Create students
            self.createStudents(school, studentsDict)
            # Create camp
            camp = self.createCamp(startDate=datetime.datetime.strptime(request.data['dates'][0], '%Y-%m-%d'),
                                   nextCampDate=datetime.datetime.strptime(request.data['dates'][1], '%Y-%m-%d'),
                                   profile=profile, school=school)
            # Create schedules
            self.createSchedules(camp, request)
            # Create Volunteers
            message = self.createVolunteers(camp, volunteersDict)
            if self.createVolunteers(camp, volunteersDict) != "Successful":
                return Response({'message': message},
                                status=status.HTTP_404_NOT_FOUND)
            # Create Camp leads
            self.createCampLeads(camp, camp_leadsDict)

            return Response({'message': 'Camp created'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Only city leads have permission to create camps'},
                            status=status.HTTP_401_UNAUTHORIZED)

    def createSchool(self, schoolDict, studentsDict, profile):
        if School.objects.filter(schoolName=schoolDict['schoolName'], pinCode=schoolDict['pinCode'],
                                 addressLine=schoolDict['addressLine']).count() == 0:  # Check if already exists
            school = School.objects.create(schoolName=schoolDict['schoolName'],
                                           addressLine=schoolDict['addressLine'],
                                           pinCode=schoolDict['pinCode'],
                                           isSatPref=schoolDict['isSatPref'], isSunPref=schoolDict['isSunPref'],
                                           city=CityLead.objects.get(profile=profile.id).city,
                                           totalStudentsCount=len(studentsDict))
        else:
            school = School.objects.get(schoolName=schoolDict['schoolName'], pinCode=schoolDict['pinCode'],
                                        addressLine=schoolDict['addressLine'])
            # Remove existing students
            for student in school.students.all():
                Student.objects.get(pk=student.id).delete()

        return school

    def createStudents(self, school, studentsDict):
        students = []
        for i in range(0, len(studentsDict)):
            students.append(
                Student(studentName=studentsDict[i]['name'], standard=studentsDict[i]['class'],
                        rollNumber=-1,
                        school=school))
        Student.objects.bulk_create(students)

    def createCamp(self, startDate, nextCampDate, profile, school):
        if Camp.objects.filter(school=school, startDate=startDate).count() == 0:  # Check if already exists
            camp = Camp.objects.create(curLevel=1,
                                       startDate=startDate,
                                       nextCampDate=nextCampDate,
                                       city=CityLead.objects.get(profile=profile).city, school=school)
        else:
            camp = Camp.objects.get(school=school,
                                    startDate=startDate)
        return camp

    def createSchedules(self, camp, request):
        schedules = []
        format_str = '%Y-%m-%d'
        for i in range(0, len(request.data['dates'])):
            date = datetime.datetime.strptime(request.data['dates'][i], format_str)
            if Schedule.objects.filter(camp=camp, campDay=i + 1).count() == 0:
                schedule = Schedule(dayOfWeek=date.weekday(),
                                    date=date, campDay=i + 1, camp=camp)
                if camp.curLevel >= 3:
                    schedule.session2StartTime = datetime.time(13, 00)
                schedules.append(schedule)
        Schedule.objects.bulk_create(schedules)

    def createCampLeads(self, camp, camp_leadsDict):
        c_leads = []
        emails = []
        for i in range(0, len(camp_leadsDict)):
            try:  # Check if camp leads's profile exists
                c_profile = Profile.objects.get(email=camp_leadsDict[i]['email'])
            except:
                self.createUser(name=camp_leadsDict[i]['name'], email=camp_leadsDict[i]['email'],
                                phoneNumber=camp_leadsDict[i]['phoneNumber'], role='CAMP_LEAD')
                c_profile = Profile.objects.get(email=camp_leadsDict[i]['email'])
            emails.append(camp_leadsDict[i]['email'])

            if CampLead.objects.filter(
                    profile=c_profile).count() == 0:  # If already present in camp leads or not
                c_leads.append(CampLead(profile=c_profile))
        CampLead.objects.bulk_create(c_leads)

        # Assign camps to camp leads
        for c in CampLead.objects.all():
            if c.profile.email in emails:
                if camp not in c.camps.all():  # Check if already assigned to the camp
                    c.camps.add(camp)
                    c.save()

    def createVolunteers(self, camp, volunteersDict):
        vols = []
        emails = []
        for i in range(0, len(volunteersDict)):
            try:  # Check if activity exists
                v_act = Activity.objects.get(activityName=volunteersDict[i]['activityName'])
            except:
                return "Activity " + volunteersDict[i]['activityName'] + " not found"

            try:  # Check if volunteer' profile exists
                v_profile = Profile.objects.get(email=volunteersDict[i]['email'])
            except:
                self.createUser(name=volunteersDict[i]['name'], email=volunteersDict[i]['email'],
                                phoneNumber=volunteersDict[i]['phoneNumber'], role='VOLUNTEER')
                v_profile = Profile.objects.get(email=volunteersDict[i]['email'])
            emails.append(volunteersDict[i]['email'])

            if Volunteer.objects.filter(
                    profile=v_profile).count() == 0:  # Check if already present in volunteers or not
                vols.append(Volunteer(isActLead=volunteersDict[i]['isActLead'],
                                      isSatPref=1, isSunPref=1,
                                      profile=v_profile, activity=v_act))
        Volunteer.objects.bulk_create(vols)

        # Assign camps to volunteers
        for v in Volunteer.objects.all():
            if v.profile.email in emails:
                if camp not in v.camps.all():  # Check if already assigned to the camp
                    v.camps.add(camp)
                    v.save()
        return "Successful"

    def createUser(self, name, email, phoneNumber, role):
        user = User.objects.create_user(username=email, email=email, password=phoneNumber)
        user.profile.name = name
        user.profile.email = email
        user.profile.phoneNumber = phoneNumber
        user.profile.userRole = role
        user.profile.save()


class DeleteCampApiView(APIView):
    def delete(self, request, campId):
        profile = request.user.profile
        camp = Camp.objects.get(pk=campId)
        if profile.userRole == "CITY_LEAD" and CityLead.objects.get(profile=profile).city == camp.city:
            school = School.objects.get(pk=camp.school.id)
            Student.objects.filter(school=school)  # Delete Students
            school.delete()  # Delete school
            camp.delete()  # Delete Camp
            return Response({"message": "Successfully deleted the camp"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have authority for this camp"}, status=status.HTTP_401_UNAUTHORIZED)


class UpdateVolunteerStatusApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, campId):
        profile = request.user.profile

        if profile.userRole == "VOLUNTEER" or "ACTIVITY_LEAD":
            volunteer = Volunteer.objects.get(profile=profile)
            camp = Camp.objects.get(pk=campId)
            nextDate = camp.nextCampDate
            schedules = camp.schedules
            campDay = 0
            for sc in schedules.all():
                if sc.date == nextDate:
                    campDay = sc.campDay
                    break

            if campDay > 0:
                profile.campDays += 1
                profile.save()
                volCampDayStatus = VolCampDayStatus(camp=Camp(pk=campId), volunteer=volunteer, campDay=campDay,
                                                    isGoing=True)
                volCampDayStatus.save()
                return Response({'message': 'Successfully updated status'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Next camp date not found in schedule'},
                                status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Only volunteers have to access to change status'},
                            status=status.HTTP_401_UNAUTHORIZED)


class ReadNotificationApiView(APIView):
    def put(self, request):
        if request.user != "AnonymousUser":
            profile = request.user.profile
            if request.data["markAllAsRead"] is True:
                for notification in profile.notifications:
                    if notification not in profile.readNotifications:
                        profile.readNotifications.add(notification)
            else:
                notification = Notification.objects.get(pk=request.data["notificationId"])
                profile.readNotifications.add(notification)
            return Response({"message": "Notification/s read"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have access"}, status=status.HTTP_401_UNAUTHORIZED)


class GetPrefsApiView(APIView):
    def get(self, request, campId):
        camp = Camp.objects.get(pk=campId)
        students = Student.objects.filter(school=camp.school)
        volunteer = Volunteer.objects.get(profile=request.user.profile)
        # All 8 activities
        if camp in volunteer.camps.all():
            modifiedJson = getStudentsPref(camp, students, campId)
        else:
            modifiedJson = {"message": "You do not have authority for this camp"}
        return Response(modifiedJson, status=status.HTTP_200_OK)


def getStudentsPref(camp, students, campId):
    if camp.curLevel == 1:
        serializer_student = StudentSerializer(students, many=True)
        extra_activities = Activity.objects.filter(activityType="EXTRA_CURR")
        co_activities = Activity.objects.filter(activityType="CO_CURR")
        serializer_extra_activity = ActivitySerializer(extra_activities, many=True)
        serializer_co_activity = ActivitySerializer(co_activities, many=True)
        level2Prefs = {}
        for student in students:
            try:
                l2Pref = Level2Pref.objects.get(student=student)
                level2Prefs[student.id] = Level2PrefSerializer(l2Pref).data
            except:
                print("Student not found in level 2 prefs")

        modifiedJson = {"Camp": campId, "StudentsList": serializer_student.data,
                        "ExtraCurricular": serializer_extra_activity.data,
                        "CoCurricular": serializer_co_activity.data, "StudentsL2Pref": level2Prefs,
                        "currLevel": camp.curLevel}
        return modifiedJson
    elif camp.curLevel == 2:
        level2Prefs = []
        for stud in students:
            try:
                l2Pref = Level2Pref.objects.get(student=stud)
                serializer = Level2PrefSerializer(l2Pref)
                level2Prefs.append(serializer.data)
            except:
                print("Student not found in level 2 prefs")

        level3Prefs = {}
        for student in students:
            try:
                l3Pref = Level2Pref.objects.get(student=student)
                level3Prefs[student.id] = Level2PrefSerializer(l3Pref).data
            except:
                print("Student not found in level 3 prefs")

        modifiedJson = {"camp": campId, "StudentsL2Pref": level2Prefs, "StudentsL3Pref": level3Prefs,
                        "currLevel": camp.curLevel}
        return modifiedJson
    elif camp.curLevel == 3:
        level3Prefs = []
        for stud in students:
            try:
                l3Pref = Level3Pref.objects.get(student=stud)
                serializer = Level3PrefSerializer(l3Pref)
                level3Prefs.append(serializer.data)
            except:
                print("Student not found in level 3 prefs")

        modifiedJson = {"camp": campId, "StudentsL3Pref": level3Prefs, "currLevel": camp.curLevel}
        return modifiedJson


class TakePrefsApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, campId):
        camp = Camp.objects.get(pk=campId)
        students = Student.objects.filter(school=camp.school)
        if camp.curLevel + 1 == 2:
            if Level2Pref.objects.filter(student=request.data['student']).count() == 0:
                level2Pref = Level2Pref(Student(student=request.data['student']))
            else:
                level2Pref = Level2Pref.objects.get(student=request.data['student'])

            content = getStudentsPref(camp, students, campId)
            level2Pref.coCurrPref1 = Activity.objects.get(pk=request.data['coCurrPref1'])
            level2Pref.coCurrPref2 = Activity.objects.get(pk=request.data['coCurrPref2'])
            level2Pref.extraCurrPref1 = Activity.objects.get(pk=request.data['extraCurrPref1'])
            level2Pref.extraCurrPref2 = Activity.objects.get(pk=request.data['extraCurrPref2'])
            level2Pref.save()
            return Response(content, status=status.HTTP_200_OK)
        elif camp.curLevel + 1 >= 3:
            if Level3Pref.objects.filter(student=request.data['student']).count() == 0:
                level3Pref = Level3Pref(student=Student(request.data['student']))
            else:
                level3Pref = Level3Pref.objects.get(student=request.data['student'])

            content = getStudentsPref(camp, students, campId)
            level3Pref.coCurrPref = Activity.objects.get(pk=request.data['coCurrPref'])
            level3Pref.extraCurrPref = Activity.objects.get(pk=request.data['extraCurrPref'])
            level3Pref.save()
            return Response(content, status=status.HTTP_200_OK)


class NotificationCreateApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, campId):
        if request.user:
            profile = request.user.profile
            if profile.userRole == 'CAMP_LEAD':
                camp = Camp.objects.get(pk=campId)
                notification = Notification(camp=camp)
                content = request.data["content"]
                notification.content = content
                notification.save()
                campLead = get_object_or_404(CampLead, profile=profile.id)
                camps = campLead.camps.all()
                i = 0
                for camp in camps:
                    # volunteer array
                    if camp.id == campId:
                        volunteers = self.getVolunteersByCamp(campId)
                        for volunteerprof in volunteers:
                            volunteerprof.notifications.add(notification)

                        campleads = self.getCampLeadsByCamp(campId)
                        for campleadprof in campleads:
                            campleadprof.notifications.add(notification)

                return Response({'message': 'Published Notification successfully'}, status=status.HTTP_201_CREATED)

    def getCampLeadsByCamp(self, campId):
        campLead_profiles = []
        campLeads = CampLead.objects.filter(camps=campId)
        for campLead in campLeads:
            campLead_profiles.append(campLead.profile)
        return campLead_profiles

    def getVolunteersByCamp(self, campId):
        volunteer_profiles = []
        volunteers = Volunteer.objects.filter(camps=campId)
        for volunteer in volunteers:
            for camp in volunteer.camps.all():
                if camp.id == campId:
                    volunteer_profiles.append(volunteer.profile)
        return volunteer_profiles


class NotificationsFetchApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user:
            profile = request.user.profile
            notificationsArr = []
            readNotifArr = []
            for notif in profile.notifications.all():
                modifiedDict = {}
                modifiedDict['school'] = notif.camp.school.schoolName
                modifiedDict['notification'] = NotificationSerializer(notif).data
                notificationsArr.append(modifiedDict)
            for readNotif in profile.readNotifications.all():
                readNotifArr.append(readNotif.id)

            return Response({"notifications": notificationsArr, "readNotifications": readNotifArr},
                            status=status.HTTP_200_OK)
        return Response({'message: No Notifications'}, status=status.HTTP_401_UNAUTHORIZED)
