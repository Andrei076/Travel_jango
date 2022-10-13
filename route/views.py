from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import connection
from route import models


def route_filter(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []
    if route_type is not None:
        query_filter.append(f"route_type ='{route_type}'")
    if country is not None:
        query_filter.append(f"country ='{country}'")
    if location is not None:
        query_filter.append(f"location ='{location}'")

    filter_string = 'and'.join(query_filter)

    joining = """SELECT
    route_route.country,
    route_route.description, 
    route_route.duration, 
    route_route.stopping, 
    route_route.route_type,
    start_point.name,
    end_point.name
    FROM route_route 
    JOIN route_place as start_point  
        On start_point.id = route_route.starting 
    JOIN route_place as end_point  
        On end_point.id = route_route.destination
WHERE """ + filter_string

    cursor.execute(joining)

    result = cursor.fetchall()
    new_result = []
    for i in result:
        new_country = i[0]
        new_description = i[1]
        new_duration = i[2]
        new_stopping = i[3]
        new_route_type = i[4]
        new_start = i[5]
        new_end = i[6]
        result_dict = {"country": new_country, "description": new_description,
                       "duration": new_duration,"stopping": new_stopping,
                       "route_type": new_route_type, "start": new_start,
                       "end": new_end}
        new_result.append(result_dict)
    return HttpResponse(new_result)


def route_detail(request, id):
    cursor = connection.cursor()
    joining = f"""SElECT
        route_route.id,
        route_route.country,
        route_route.location,
        route_route.description, 
        route_route.duration, 
        route_route.stopping, 
        route_route.route_type,
        start_point.name,
        end_point.name
        
        FROM route_route
        JOIN route_place as start_point
        ON start_point.id = route_route.starting
        JOIN route_place as end_point  
        On end_point.id = route_route.destination
        WHERE route_route.id = {id}"""

    cursor.execute(joining)
    result = cursor.fetchall()
    new_result = [
        {'route_id': itm[0], 'country': itm[1],'location': itm[2],
         'description': itm[3],'duration': itm[4],'stopping': itm[5],
         'route_type': itm[6], 'start': itm[7],'end': itm[8]} for itm in result]
    return HttpResponse(new_result)


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
    cursor = connection.cursor()
    joining = f"""SElECT
        event.id,
        event.start_date,
        event.price,
        start_point.name,
        end_point.name,
        route.country,
        route.location,
        route.stopping,
        route.duration,
        route.route_type
        FROM route_event as event
        JOIN route_place as start_point
        ON start_point.id = route.starting
        JOIN route_place as end_point  
        On end_point.id = route.destination
        JOIN route_route as route 
        ON event.route_id =route.id
        WHERE event.id = {event_id}
    """
    cursor.execute(joining)
    result = cursor.fetchall()

    new_result = [{'event_id': itm[0], 'start_date': itm[1], 'price': itm[2],
                   'start': itm[3], 'end': itm[4],  'country': itm[5],
                   'location': itm[6], 'stopping': itm[7], 'duration': itm[
            8],    'route_type': itm[9]} for itm
                  in result]

    return HttpResponse(new_result)


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
