from django.contrib import admin
from django.urls import path
from sattle import views  # Import the views from the app


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/view-guesses/', views.view_guesses, name='view-guesses'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('submit_guess/', views.submit_guess, name='submit_guess'),
    path('reset_score/', views.reset_score, name='reset_score'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('save_global_high_score/', views.save_global_high_score, name='save_global_high_score'),
    path('get_global_high_scores/', views.get_global_high_scores, name='get_global_high_scores'),
    path('restart/', views.restart, name='restart'),
]

if settings.DEBUG:  # Only serve media files in debug mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
