from django.contrib import admin
from .models import Parcel, ParcelStatusHistory, PostOffice


class ParcelStatusHistoryInline(admin.TabularInline):
    model = ParcelStatusHistory
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = [
        "tracking_number",
        "sender_full_name",
        "receiver_full_name",
        "status",
        "sender_office",
        "destination_office",
        "created_at",
    ]
    list_filter = ["status", "sender_office", "destination_office"]
    search_fields = [
        "tracking_number",
        "sender_full_name",
        "receiver_full_name",
        "sender_phone",
        "receiver_phone",
    ]
    readonly_fields = ["tracking_number", "created_at"]
    inlines = [ParcelStatusHistoryInline]


@admin.register(PostOffice)
class PostOfficeAdmin(admin.ModelAdmin):
    list_display = ["number", "city", "address", "postal_code"]
    search_fields = ["number", "city", "address", "postal_code"]
    list_filter = ["city"]


@admin.register(ParcelStatusHistory)
class ParcelStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["parcel", "status", "office", "created_at"]
    list_filter = ["status", "office", "created_at"]
    search_fields = ["parcel__tracking_number", "comment"]