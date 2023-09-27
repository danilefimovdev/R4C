from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from robots import views

urlpatterns = [
    path('', csrf_exempt(views.RobotView.as_view()), name='robots'),
    path('get_week_report_xlsx/', views.get_week_report_xlsx, name='get-week-report'),
]