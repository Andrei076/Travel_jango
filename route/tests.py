from django.test import TestCase, RequestFactory
from django.test import Client
from route.models import Review, Event
from route.views import add_event_route


class TestReview(TestCase):
    def test_review(self):
        review = Review(
            route_id=2,
            review_text='test',
            review_rate=5
        )
        review.save()
        client = Client()
        response = client.get(f'/route/2/review')
        self.assertEqual(200, response.status_code)


class TestEvent(TestCase):
    def test_annonimus_user(self):
        client = Client()
        response = client.get('/route/1/add_event')
        self.assertEqual(401, response.status_code)

        response_client_post = client.post('/route/1/add_event')
        self.assertEqual(401, response_client_post.status_code)

    def setUp(self):
        self.factory = RequestFactory()

        class userMock():
            def has_perm(self, *args, **kwargs):
                return True

        self.user = userMock()

    def test_with_user(self):
        request = self.factory.post('/route/3/add_event',
                                    {'start_date': "2023-06-07",
                                     'price': 300})
        request.user = self.user
        route_id = 3
        response = add_event_route(request, route_id)
        self.assertEqual(200, response.status_code)
