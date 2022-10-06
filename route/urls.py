from django.urls import path
from . import views

app_name = "route"

urlpatterns = [
    path('', views.route_filter, name='routes'),
    path('add_route', views.add_route, name='add_route'),
    path('<int:id>', views.route_detail, name='route'),
    path('<int:route_id>/review', views.route_review, name='route_review'),
    path('<int:route_id>/add_event', views.add_event_route,
         name='add_event_route'),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter,
         name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter,
         name='route_location'),
]