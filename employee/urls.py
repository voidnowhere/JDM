from django.urls import path, re_path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^users/search/(?P<search>((id|first_name|last_name|email|phone)=(\w+[\-\.]*\w+@?\w+\-?\w+\.?\w+|\w+))?)/(?P<setof>(10|25|50|100))/(?P<num_page>[1-9]\d*)', views.users, name='users'),
    path("cars/",views.cars, name="cars"),
    path("car/<int:id>",views.car ,name="car"),
]
