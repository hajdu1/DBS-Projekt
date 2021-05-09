from django.conf.urls import url

from . import views

urlpatterns = [
    url('health/', views.health),
    url(r'^ov/submissions/(.*)', views.submissions),
    url('companies/', views.companies)
]
