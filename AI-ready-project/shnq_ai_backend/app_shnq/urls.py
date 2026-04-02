from django.urls import path

from .views.api import ChatAPIView
from .views.sync import sync_document, delete_document

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="api-chat"),
    path("sync-document/", sync_document, name="sync-document"),
    path("documents/<str:code>/", delete_document, name="delete-document"),
]
