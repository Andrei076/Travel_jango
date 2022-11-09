from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from route import models
from mongo_utils import MongoDBConnection
import json
from bson import ObjectId

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
        new_duration = i[1]
        new_stopping = i[2]
        new_route_type = i[3]
        new_start = i[4]
        new_end = i[5]
        result_dict = {"country": new_country,
                       "duration": new_duration,"stopping": new_stopping,
                       "route_type": new_route_type, "start": new_start,
                       "end": new_end}
        new_result.append(result_dict)

    p = Paginator(new_result, 2)
    num_page = int(request.GET.get('page', default=1))

    if p.num_pages < num_page:
        num_page = 1

    select_page = p.get_page(num_page)

    return HttpResponse(select_page.object_list)


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

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['stop_points']
        stop_point = collec.find_one({'_id': ObjectId(new_result[0][
                                                          'stopping'])})
    return HttpResponse([new_result, stop_point])


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
            stopping = request.POST.get('stopping')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_type = request.POST.get('route_type')

            models.validate_stopping_point(stopping)
            stop_list = json.loads(stopping)

            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collec = db['stop_points']
                id_stop_points = collec.insert_one({'points': stop_list}).inserted_id

            start_obj = models.Place.objects.get(name=starting)
            dest_obj = models.Place.objects.get(name=destination)
            new_route = models.Route(location=location,starting=start_obj.id,
                         destination=dest_obj.id,country=country,
                         stopping=id_stop_points,
                         description=description,duration=duration,
                         route_type=route_type)
            new_route.full_clean()
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
                         price=price, event_admin=1)
            try:
                new_event.full_clean()
                new_event.save()
            except ValidationError:
                return HttpResponse('error Date')

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
        route.route_type,
        event.event_users
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
            8],    'route_type': itm[9], 'id_event_users': itm[10]} for itm
                  in result]

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['event_users']
        id_users = collec.find_one({'_id': ObjectId(new_result[0][
                                                       'id_event_users'])})
    users_accepted = User.objects.filter(pk__in=id_users['accepted'])
    users_pending = User.objects.filter(pk__in=id_users['pending'])

    list_users_accepted = [{itm.id: itm.username} for itm in users_accepted]
    list_users_pending = [{itm.id: itm.username} for itm in users_pending]

    new_result[0]['users_accepted'] = list_users_accepted
    new_result[0]['users_pending'] = list_users_pending

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


def add_me_to_event(request, event_id):
    user = request.user.id
    event = models.Event.objects.filter(id=event_id).first()

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        event_users = db["event_users"]
        all_event_users = event_users.find_one(
            {'_id': ObjectId(event.event_users)})
        if user in all_event_users['pending'] or user in all_event_users[
            'accepted']:
            return HttpResponse('You are in pending users')
        else:
            all_event_users['pending'].append(user)
            event_users.update_one({'_id': ObjectId(event.event_users)},
                                   {"$set": all_event_users}, upsert=False)

    return HttpResponse('ok. You are added')


def event_accept_user(request, event_id):
    if request.method == "GET":
        if request.user.is_superuser:
            event = models.Event.objects.filter(id=event_id).first()
            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collec = db['event_users']
                all_event_users = collec.find_one(
                    {'_id': ObjectId(event.event_users)})
            return render(request, "accepted_user.html", {"pending_users":
                                                              all_event_users['pending']})

        else:
            return HttpResponse("You dont have access to this!")

    if request.method == "POST":
        if request.POST.get("selected_user_id") is not None:
            event = models.Event.objects.filter(id=event_id).first()
            select_user = int(request.POST.get("selected_user_id"))
            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collec = db['event_users']
                all_event_users = collec.find_one(
                    {'_id': ObjectId(event.event_users)})

                all_event_users["pending"].remove(select_user)
                all_event_users["accepted"].append(select_user)

                collec.update_one({'_id': ObjectId(event.event_users)},
                                  {"$set": all_event_users}, upsert=False)

            return HttpResponse("User is accepted")
        else:
            return HttpResponse("You do not choose user")
