from django.urls import path
from . import views
urlpatterns = [
    path('',views.editor,name="editor"),
    path("submit/",views.submit,name="submit"),
    path("result/<uuid:pk>/",views.result,name="result"),
]