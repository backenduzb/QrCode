from django.urls import path
from .views import access_doc

urlpatterns = [
    path('d/<int:pk>/', access_doc, name='doc-access'),
]
