from rest_framework import generics, status
from rest_framework.response import Response
from .models import Parcel, PostOffice
from .serializers import ParcelCreateSerializer, ParcelDetailSerializer,ParcelListSerializer, ParcelStatusUpdateSerializer, PostOfficeSerializer


# View for creating and listing post offices
class PostOfficeListCreateView(generics.ListCreateAPIView):
    queryset = PostOffice.objects.all()
    serializer_class = PostOfficeSerializer




# View for creating parcels and listing parcels
class ParcelListCreateView(generics.ListCreateAPIView):
    queryset = Parcel.objects.select_related("sender_office", "destination_office")


    # Use different serializers for create and list actions
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ParcelCreateSerializer
        return ParcelListSerializer


    # Add simple filtering by status and sender city
    def get_queryset(self):
        queryset = super().get_queryset()

        status_param = self.request.query_params.get("status")
        from_city = self.request.query_params.get("from_city")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if from_city:
            queryset = queryset.filter(sender_office__city__iexact=from_city)

        return queryset


# View for getting parcel details by tracking number
class ParcelDetailView(generics.RetrieveAPIView):
    queryset = Parcel.objects.select_related(
        "sender_office",
        "destination_office",
    ).prefetch_related("history")
    serializer_class = ParcelDetailSerializer
    lookup_field = "tracking_number"
    lookup_url_kwarg = "tracking_number"



# View for changing parcel status
class ParcelStatusUpdateView(generics.GenericAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelStatusUpdateSerializer
    lookup_field = "tracking_number"
    lookup_url_kwarg = "tracking_number"

    def post(self, request, *args, **kwargs):
        parcel = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            context={"parcel": parcel},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        parcel.refresh_from_db()
        response_serializer = ParcelDetailSerializer(parcel)
        return Response(response_serializer.data, status=status.HTTP_200_OK)




# View for parcels that are currently in a specific post office
class PostOfficeParcelsView(generics.ListAPIView):
    serializer_class = ParcelListSerializer

    def get_queryset(self):
        return Parcel.objects.select_related(
            "sender_office",
            "destination_office",
        ).filter(
            status=Parcel.Status.ARRIVED,
            destination_office_id=self.kwargs["pk"],
        )