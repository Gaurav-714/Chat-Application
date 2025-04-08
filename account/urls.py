from django.urls import path
from .views import *

urlpatterns = [
    path('signup', sign_up, name='sign-up'),
    path('signin', sign_in, name='sign-in'),
]
