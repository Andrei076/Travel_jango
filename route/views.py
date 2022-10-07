from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from route import models


def route_filter(request, route_type=None, country=None, location=None):
    query_filter = {}
    if route_type is not None:
        query_filter['route_type'] = route_type
    if country is not None:
        query_filter['country'] = country
    if location is not None:
        query_filter['location'] = location
    result = models.Route.objects.all().filter(**query_filter)
    print(result)
    return HttpResponse([{'country': itm.country, 'id': itm.id} for itm in
                         result])


def route_detail(request, id):
    result = models.Route.objects.all().filter(id=id)
    return HttpResponse([{'country': itm.country, 'id': itm.id} for
                         itm in result])


def route_review(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    return HttpResponse(
        [{'route_id': itm.route_id, 'review_rate': itm.review_rate} for itm in
         result])


def add_route(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            return render(request, 'add_route.html')
        if request.method == 'POST':
            starting = request.POST.get('starting')
            destination = request.POST.get('destination')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_type = request.POST.get('route_type')
            start_obj = models.Place.objects.get(name=starting)
            dest_obj = models.Place.objects.get(name=destination)
            new_route = models.Route(location=location,starting=start_obj.id,
                         destination=dest_obj.id,country=country,
                         description=description,duration=duration,
                         route_type=route_type, stopping={})
            new_route.save()
            return HttpResponse('Creating a route')
    else:
        return HttpResponse('Not allowed to add route')


def add_event_route(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event_route.html')
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            new_event = models.Event(route_id=route_id, start_date=start_date,
                         price=price, approved_user=[], pending_users=[],
                                     event_admin=1)
            new_event.save()
            return HttpResponse('Info about event')
    else:
        return HttpResponse('Not allowed to add event')

def event_handler(request, event_id):
    result = models.Event.objects.all().filter(id=event_id)
    return HttpResponse([{'route_id': itm.route_id, 'start_date': itm.start_date,
                          'price': itm.price} for itm in result])


def main_page(request):
    return HttpResponse('Travel')


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse('User is login')
            else:
                return HttpResponse('No user')
    else:
        return HttpResponse('<a href="logout" > logout</a>')


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'registration.html')
        if request.method == 'POST':
            user = User.objects.create_user(username=request.POST.get('username'),
                                            password=request.POST.get('password'),
                                            email=request.POST.get('email'),
                                            first_name=request.POST.get('first_name'),
                                            last_name=request.POST.get('last_name'))
            user.save()
            return HttpResponse('User is create')
    else:
        return HttpResponse('<a href="logout" > logout</a>')


def logout_user(request):
    logout(request)
    return redirect('/login')
