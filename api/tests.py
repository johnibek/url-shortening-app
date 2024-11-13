from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from .models import UrlModel
from datetime import timezone
import pytz
from django.core.exceptions import ValidationError


class UrlShorteningServiceAPITestCase(APITestCase):
    def test_homepage(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "Hello world")

    def test_create_short_url(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        response = self.client.post("/api/shorten/", data=data)
        shortened_url = UrlModel.objects.get(url=data['url'])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['short_code']), 6)
        self.assertEqual(response.data['url'], shortened_url.url)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
        self.assertEqual(shortened_url.access_count, 0)

    def test_duplicate_short_url(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        new_shortened_url = UrlModel.objects.create(url=data['url'])

        response = self.client.post('/api/shorten/', data=data)

        url_count = UrlModel.objects.count()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'This url has already been shortened. Short code: {}'.format(new_shortened_url.short_code))
        self.assertEqual(url_count, 1)
        self.assertNotIn('url', response.data)
        self.assertNotIn('short_code', response.data)
        self.assertNotIn('created_at', response.data)
        self.assertNotIn('updated_at', response.data)
        self.assertNotIn('access_count', response.data)

    def test_invalid_url_shortening(self):
        data = {
            "url": "www.github.com/johnibek"
        }
        response = self.client.post("/api/shorten/", data=data)

        url_count = UrlModel.objects.count()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['url'][0], "Enter a valid URL.")
        self.assertEqual(url_count, 0)

    def test_get_short_url(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        short_url = UrlModel.objects.create(url=data['url'])

        response = self.client.get(reverse("api:get_shortened_url", kwargs={'short_code': short_url.short_code}))
        count = UrlModel.objects.count()

        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['url'], short_url.url)
        self.assertEqual(response.data['short_code'], short_url.short_code)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)
        self.assertNotIn('access_count', response.data)

    def test_get_wrong_short_url_error(self):
        response = self.client.get(reverse("api:get_shortened_url", kwargs={'short_code': "abc123"}))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "short code not found")

    def test_delete_short_url(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        short_url = UrlModel.objects.create(url=data['url'])

        response = self.client.delete(reverse("api:delete_short_url", kwargs={'short_code': short_url.short_code}))

        count = UrlModel.objects.all().count()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(count, 0)
        self.assertIsNone(response.data)

    def test_delete_non_existent_short_url(self):
        response = self.client.delete(reverse("api:delete_short_url", kwargs={'short_code': 'abc123'}))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], 'short code not found')
        self.assertNotIn('url', response.data)
        self.assertNotIn('short_code', response.data)
        self.assertNotIn('created_at', response.data)
        self.assertNotIn('updated_at', response.data)

    def test_update_short_url(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        updated_data = {
            "url": "https://github.com/johnibek?tab=repositories"
        }
        invalid_data = {
            "url": "github.com/johnibek?tab=repositories"
        }
        short_url = UrlModel.objects.create(url=data['url'])

        response = self.client.put(reverse("api:update_short_url", kwargs={'short_code': short_url.short_code}), data=updated_data)
        response_invalid_url = self.client.put(reverse("api:update_short_url", kwargs={"short_code": short_url.short_code}), data=invalid_data)

        short_url.refresh_from_db()

        tz = pytz.timezone("Asia/Tashkent")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['url'], short_url.url)
        self.assertNotEqual(response.data['url'], data['url'])
        self.assertEqual(response.data['short_code'], short_url.short_code)
        self.assertEqual(response.data['created_at'], short_url.created_at.astimezone(tz).isoformat())
        self.assertEqual(response.data['updated_at'], short_url.updated_at.astimezone(tz).isoformat())
        self.assertNotIn("access_count", response.data)

        self.assertEqual(response_invalid_url.status_code, 400)
        self.assertEqual(response_invalid_url.data['url'], ["Enter a valid URL."])

    def test_update_non_existent_url(self):
        updated_url = {
            "url": "https://github.com/johnibek?tab=repositories"
        }
        response = self.client.put(reverse("api:update_short_url", kwargs={'short_code': "abc123"}), data=updated_url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], "No UrlModel matches the given query.")

    def test_redirect_url(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        url_obj = UrlModel.objects.create(url=data['url'])

        response = self.client.get(reverse('api:redirect_url', kwargs={'short_code': url_obj.short_code}))
        count = UrlModel.objects.count()

        url_obj.refresh_from_db()

        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(url_obj.access_count, 1)

    def test_redirect_non_existent_url(self):
        response = self.client.get(reverse('api:redirect_url', kwargs={'short_code': "abc123"}))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], "No UrlModel matches the given query.")

    def test_get_url_stats(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        url_obj = UrlModel.objects.create(url=data['url'])
        response1 = self.client.get(reverse('api:redirect_url', kwargs={'short_code': url_obj.short_code}))
        response2 = self.client.get(reverse('api:url_stats', kwargs={'short_code': url_obj.short_code}))

        url_obj.refresh_from_db()

        tz = pytz.timezone("Asia/Tashkent")

        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['access_count'], 1)
        self.assertEqual(response2.data['url'], url_obj.url)
        self.assertEqual(response2.data['short_code'], url_obj.short_code)
        self.assertEqual(response2.data['created_at'], url_obj.created_at.astimezone(tz).isoformat())
        self.assertEqual(response2.data['updated_at'], url_obj.updated_at.astimezone(tz).isoformat())

    def test_model_str_function(self):
        data = {
            "url": "https://www.github.com/johnibek"
        }
        url_obj = UrlModel.objects.create(url=data['url'])

        self.assertEqual(str(url_obj), url_obj.short_code)

    def test_app_name(self):
        from api import urls
        self.assertEqual(urls.app_name, 'api')