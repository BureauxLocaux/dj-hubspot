from django.urls import path

from djhubspot.views import WebhookView


urlpatterns = [
    path('webhook/', WebhookView.as_view(), name='webhook'),
]
