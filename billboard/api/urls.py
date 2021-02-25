from django.urls import path

from .views import posters
from .views import PosterDetailView
from .views import comments

urlpatterns = [
    path('posters/<int:pk>/comments/', comments),
    path('posters/<int:pk>', PosterDetailView.as_view()),
    path('posters/', posters),
]