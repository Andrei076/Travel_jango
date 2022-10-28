from django.urls import path
from . import views

app_name = "route"

urlpatterns = [
    path('', views.route_filter, name='routes'),
    path('<int:id>', views.route_detail, name='route_detail'),
    path('<int:route_id>/review', views.route_review, name='route_review'),
    path('<int:route_id>/add_event', views.add_event_route,
         name='add_event_route'),
    path('add_route', views.add_route, name='add_route'),
    path("event/<event_id>/add_me", views.add_me_to_event, name='add_me'),
    path("event/<event_id>/accept_user", views.event_accept_user,
         name='accept_user'),
    path('<str:route_type>/', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>/', views.route_filter,
         name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>/', views.route_filter,
         name='route_location')
]