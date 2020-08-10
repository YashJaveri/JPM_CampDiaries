"""JPM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', ProfileApiView.as_view()),
    path('changePassword/', ChangePassword.as_view()),
    path('camps/<int:passedCityId>/', CampByCityApiView.as_view()),
    path('camps/', CampsApiView.as_view()),
    path('campInfo/<int:campId>', CampInfoApiView.as_view()),
    path('createCamp/', CreateCampApiView.as_view()),
    path('publishSchedule/<int:campId>', PublishScheduleApiView.as_view()),
    path('generateBatches/', GenerateBatchesApiView.as_view()),
    path('updateLevel/', UpdateLevelApiView.as_view()),
    path('attend/<int:campId>', UpdateVolunteerStatusApiView.as_view()),
    path('getPrefs/<int:campId>', GetPrefsApiView.as_view()),
    path('takePrefs/<int:campId>', TakePrefsApiView.as_view()),
    path('createNotification/<int:campId>', NotificationCreateApiView.as_view()),
    path('fetchNotifications/', NotificationsFetchApiView.as_view()),
    path('markAsRead/', ReadNotificationApiView.as_view()),
    path('deleteCamp/<int:campId>', DeleteCampApiView.as_view())
]