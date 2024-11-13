from django.urls import path
from . import views

app_name='api'
urlpatterns = [
    path("", views.home, name='home'),
    path("shorten/", views.create_short_url, name="create_short_url"),
    path("shortened_urls/<str:short_code>", views.get_update_delete_short_url, name='get_shortened_url'),
    path("shortened_urls/<str:short_code>", views.get_update_delete_short_url, name='update_short_url'),
    path("shortened_urls/<str:short_code>", views.get_update_delete_short_url, name='delete_short_url'),
    path("shortened_urls/<str:short_code>/stats", views.get_url_stats, name='url_stats'),
    path("shortened_urls/<str:short_code>/redirect", views.redirect_url, name='redirect_url'),
]
