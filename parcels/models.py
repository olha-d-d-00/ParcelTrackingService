from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def generate_tracking_number():
    return f"TRK{uuid.uuid4().hex[:10].upper()}"


class PostOffice(models.Model):
    number = models.PositiveIntegerField(unique=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    class Meta:
        ordering = ["city", "number"]

    def __str__(self):
        return f"Office #{self.number} - {self.city}"


class Parcel(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        ACCEPTED = "accepted", "Accepted"
        IN_TRANSIT = "in_transit", "In transit"
        ARRIVED = "arrived", "Arrived"
        DELIVERED = "delivered", "Delivered"
        RETURNED = "returned", "Returned"

    TERMINAL_STATUSES = {Status.DELIVERED, Status.RETURNED}

    tracking_number = models.CharField(
        max_length=32,
        unique=True,
        default=generate_tracking_number,
        editable=False,
    )

    sender_full_name = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=20)

    receiver_full_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=20)

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("30.00")),
        ],
    )
    declared_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    sender_office = models.ForeignKey(
        PostOffice,
        on_delete=models.PROTECT,
        related_name="sent_parcels",
    )
    destination_office = models.ForeignKey(
        PostOffice,
        on_delete=models.PROTECT,
        related_name="destination_parcels",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.sender_office_id and self.sender_office_id == self.destination_office_id:
            raise ValidationError("Sender and destination offices must be different.")

    def __str__(self):
        return self.tracking_number


class ParcelStatusHistory(models.Model):
    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="history",
    )
    status = models.CharField(max_length=20, choices=Parcel.Status.choices)
    office = models.ForeignKey(
        PostOffice,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.parcel.tracking_number}: {self.status}"