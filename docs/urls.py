from django.urls import path
from .views import access_doc

app_name = "documents"  

urlpatterns = [
    path("d/<str:code>/", access_doc, name="doc-access"),
]