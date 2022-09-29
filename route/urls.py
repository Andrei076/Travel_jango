from django.urls import path
from . import views

app_name = "route"

urlpatterns = [
    path('', views.route_filter, name='routes'),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter,
         name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter,
         name='route_location'),

    path('add_route', views.add_route, name='add_route'),
    path('<int:id_route>', views.route_detail, name='route_detail'),
    path('<int:id_route>/review', views.review_route, name='review_route'),
    path('<int:id_route>/add_event', views.add_event_route, name='add_event_route'),
]