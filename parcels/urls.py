from django.urls import path
from .views import ParcelDetailView, ParcelListCreateView,ParcelStatusUpdateView, PostOfficeListCreateView,PostOfficeParcelsView


urlpatterns = [
    path("offices/", PostOfficeListCreateView.as_view(), name="office-list"),
    path("offices/<int:pk>/parcels/", PostOfficeParcelsView.as_view(), name="office-parcels"),
    path("parcels/", ParcelListCreateView.as_view(), name="parcel-list"),
    path("parcels/<str:tracking_number>/", ParcelDetailView.as_view(), name="parcel-detail"),
    path("parcels/<str:tracking_number>/status/", ParcelStatusUpdateView.as_view(), name="parcel-status-update")
]