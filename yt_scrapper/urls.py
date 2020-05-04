from django.conf.urls import url
from yt_scrapper import views

urlpatterns = [
    url(r'^home/$',views.greetings),
    url(r'^home/search$',views.search),
    url(r'^home/search/top-videos$',views.top_videos),
]
