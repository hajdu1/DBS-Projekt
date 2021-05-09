from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ov/submissions/(.*)', views.submissions_v2),
    url('companies/', views.companies_v2)
]
