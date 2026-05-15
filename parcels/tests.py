from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Parcel, PostOffice


class ParcelApiTests(APITestCase):
    def setUp(self):
        self.sender_office = PostOffice.objects.create(
            number=1,
            city="Kyiv",
            address="Khreshchatyk 1",
            postal_code="01001",
        )
        self.destination_office = PostOffice.objects.create(
            number=2,
            city="Lviv",
            address="Market Square 2",
            postal_code="79000",
        )

    def create_parcel(self):
        url = reverse("parcel-list")
        data = {
            "sender_full_name": "Maria Melnyk",
            "sender_phone": "+380991112233",
            "receiver_full_name": "Mykola Melnyk",
            "receiver_phone": "+380991234567",
            "sender_office": self.sender_office.id,
            "destination_office": self.destination_office.id,
            "weight": "2.50",
            "declared_value": "100.00",
        }
        return self.client.post(url, data, format="json")

    def test_create_parcel(self):
        response = self.create_parcel()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Parcel.objects.count(), 1)
        self.assertEqual(Parcel.objects.first().status, Parcel.Status.CREATED)
        self.assertTrue(Parcel.objects.first().tracking_number.startswith("TRK"))
        self.assertEqual(Parcel.objects.first().history.count(), 1)

    def test_same_offices_are_not_allowed(self):
        url = reverse("parcel-list")
        data = {
            "sender_full_name": "Vasya Test",
            "sender_phone": "+380991112233",
            "receiver_full_name": "Petya Test",
            "receiver_phone": "+380991234567",
            "sender_office": self.sender_office.id,
            "destination_office": self.sender_office.id,
            "weight": "2.50",
            "declared_value": "100.00",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delivered_without_arrived_is_not_allowed(self):
        self.create_parcel()
        parcel = Parcel.objects.first()

        url = reverse("parcel-status-update", args=[parcel.tracking_number])

        response = self.client.post(
            url,
            {
                "status": Parcel.Status.DELIVERED,
                "office": self.destination_office.id,
                "comment": "Trying to deliver too early",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_terminal_status_cannot_be_changed_after_delivered(self):
        self.create_parcel()
        parcel = Parcel.objects.first()

        url = reverse("parcel-status-update", args=[parcel.tracking_number])

        self.client.post(
            url,
            {
                "status": Parcel.Status.ACCEPTED,
                "office": self.sender_office.id,
                "comment": "Accepted at sender office",
            },
            format="json",
        )
        self.client.post(
            url,
            {
                "status": Parcel.Status.IN_TRANSIT,
                "office": self.sender_office.id,
                "comment": "Sent to destination",
            },
            format="json",
        )
        self.client.post(
            url,
            {
                "status": Parcel.Status.ARRIVED,
                "office": self.destination_office.id,
                "comment": "Arrived at destination office",
            },
            format="json",
        )
        self.client.post(
            url,
            {
                "status": Parcel.Status.DELIVERED,
                "office": self.destination_office.id,
                "comment": "Delivered to receiver",
            },
            format="json",
        )

        response = self.client.post(
            url,
            {
                "status": Parcel.Status.RETURNED,
                "office": self.destination_office.id,
                "comment": "Trying to change terminal status",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_terminal_status_cannot_be_changed_after_returned(self):
        self.create_parcel()
        parcel = Parcel.objects.first()

        url = reverse("parcel-status-update", args=[parcel.tracking_number])

        self.client.post(
            url,
            {
                "status": Parcel.Status.RETURNED,
                "office": self.sender_office.id,
                "comment": "Returned to sender",
            },
            format="json",
        )

        response = self.client.post(
            url,
            {
                "status": Parcel.Status.IN_TRANSIT,
                "office": self.sender_office.id,
                "comment": "Trying to change returned parcel",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weight_must_be_positive_and_not_more_than_30(self):
        url = reverse("parcel-list")
        data = {
            "sender_full_name": "Olga Test",
            "sender_phone": "+380991112233",
            "receiver_full_name": "Den Test",
            "receiver_phone": "+380991234567",
            "sender_office": self.sender_office.id,
            "destination_office": self.destination_office.id,
            "weight": "31.00",
            "declared_value": "100.00",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_declared_value_cannot_be_negative(self):
        url = reverse("parcel-list")
        data = {
            "sender_full_name": "Katya Melnyk",
            "sender_phone": "+380991112233",
            "receiver_full_name": "Dima Core",
            "receiver_phone": "+380991234567",
            "sender_office": self.sender_office.id,
            "destination_office": self.destination_office.id,
            "weight": "2.50",
            "declared_value": "-1.00",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)