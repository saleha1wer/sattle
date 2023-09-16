from django.contrib import admin
from django.urls import path
from sattle import views  # Import the views from the app


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Define the app's URL patterns here
    path('submit_guess/', views.submit_guess, name='submit_guess'),
     path('reset_score/', views.reset_score, name='reset_score'),
]

if settings.DEBUG:  # Only serve media files in debug mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
