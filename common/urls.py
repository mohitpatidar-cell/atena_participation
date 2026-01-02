from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('provider-summary-upload/', ProviderSummaryUploadView.as_view(),name='provider_summary_upload'),
  
]
