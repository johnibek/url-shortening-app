from django.urls import path
from . import views

app_name = 'url'
urlpatterns = [
    path('', views.CreateShortUrl.as_view(), name='create_short_url'),
    path('<str:short_code>', views.GetShortenedURL.as_view(), name='get_short_url'),
    path('<str:short_code>/redirect', views.RedirectShortUrl.as_view(), name='redirect_short_url'),
    path('<str:short_code>/count', views.UrlAccessCount.as_view(), name='url_access_count'),
    path('track/', views.TrackShortUrl.as_view(), name='track_short_url'),
    path('unshorten/', views.UnshortenUrl.as_view(), name='unshorten_url'),
]