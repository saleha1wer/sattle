from django.urls import path
from . import views

app_name = 'sattle'

urlpatterns = [
    # Define the URL pattern for the app's home view
    path('', views.home, name='home'),

    # Define the URL pattern for the app's submit_guess view
    path('submit_guess/', views.submit_guess, name='submit_guess'),

    path('reset_score/', views.reset_score, name='reset_score'),
]

