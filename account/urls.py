from django.urls import path
from .views import *

urlpatterns = [
    path('signup', registerView, name='sign-up'),
    path('signin', loginView, name='sign-in'),
]
