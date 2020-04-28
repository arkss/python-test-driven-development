from django.urls import reverse, resolve
from django.test import TestCase
from django.http import HttpRequest
from .views import home_page
from django.shortcuts import render
from django.template.loader import render_to_string
from lists.models import Item, List
import re


class HomePageTest(TestCase):
    def remove_csrf(self, origin):
        csrf_regex = r"<input[^>]+csrfmiddlewaretoken[^>]+>"
        return re.sub(csrf_regex, "", origin)

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)

        expected_html = self.remove_csrf(render_to_string("home.html", request=request))
        response_decode = self.remove_csrf(response.content.decode())

        self.assertEqual(response_decode, expected_html)


class ItemModelTest(TestCase):
    def remove_csrf(self, origin):
        csrf_regex = r"<input[^>]+csrfmiddlewaretoken[^>]+>"
        return re.sub(csrf_regex, "", origin)

    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = "첫 번째 아이템"
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = "두 번째 아이템"
        second_item.list = list_
        second_item.save()

        save_items = Item.objects.all()
        self.assertEqual(save_items.count(), 2)

        first_saved_item = save_items[0]
        second_saved_item = save_items[1]

        self.assertEqual(first_saved_item.text, "첫 번째 아이템")
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, "두 번째 아이템")
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        response = self.client.get("/lists/the-only-list-in-the-world/")

        self.assertTemplateUsed(response, "list.html")

    def test_displays_all_items(self):
        list_ = List.objects.create()
        Item.objects.create(text="itemey 1", list=list_)
        Item.objects.create(text="itemey 2", list=list_)


class NewListTest(TestCase):
    def test_saving_a_POST_request(self):
        self.client.post("/lists/new", data={"item_text": "신규 작업 아이템"})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()

        self.assertEqual(new_item.text, "신규 작업 아이템")

    def test_redirects_after_POST(self):
        response = self.client.post("/lists/new", data={"item_text": "신규 작업 아이템"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/lists/the-only-list-in-the-world/")