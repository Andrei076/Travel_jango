from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def route_filter(request, route_type=None, country=None, location=None):
    return HttpResponse('Ok')


def route_detail(request, id_route):
    return HttpResponse('Ok')


def review_route(request, id_route):
    return HttpResponse('Ok')


def add_route(request):
    return HttpResponse('Ok')


def add_event_route(request, id_route):
    return HttpResponse('Ok')


def event_handler(request, event_id):
    return HttpResponse('Ok')


def main_page(request):
    return HttpResponse('Travel')