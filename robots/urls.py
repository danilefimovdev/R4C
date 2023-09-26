from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from robots import views

urlpatterns = [
    path('', csrf_exempt(views.RobotView.as_view()), name='robots'),
]