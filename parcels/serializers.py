from rest_framework import serializers
from .models import Parcel, ParcelStatusHistory, PostOffice



# Serializer for post offices
class PostOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostOffice
        fields = ["id", "number", "city", "address", "postal_code"]



# Serializer for parcel status history
class ParcelStatusHistorySerializer(serializers.ModelSerializer):
    office = PostOfficeSerializer(read_only=True)

    class Meta:
        model = ParcelStatusHistory
        fields = ["id", "status", "office", "comment", "created_at"]



# Serializer for parcel list endpoint
class ParcelListSerializer(serializers.ModelSerializer):
    sender_office = PostOfficeSerializer(read_only=True)
    destination_office = PostOfficeSerializer(read_only=True)

    class Meta:
        model = Parcel
        fields = [
            "id",
            "tracking_number",
            "sender_full_name",
            "sender_phone",
            "receiver_full_name",
            "receiver_phone",
            "sender_office",
            "destination_office",
            "weight",
            "declared_value",
            "status",
            "created_at",
        ]



# Detailed serializer with parcel history
class ParcelDetailSerializer(ParcelListSerializer):
    history = ParcelStatusHistorySerializer(many=True, read_only=True)

    class Meta(ParcelListSerializer.Meta):
        fields = ParcelListSerializer.Meta.fields + ["history"]




# Serializer for parcel creation
class ParcelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = [
            "id",
            "tracking_number",
            "sender_full_name",
            "sender_phone",
            "receiver_full_name",
            "receiver_phone",
            "sender_office",
            "destination_office",
            "weight",
            "declared_value",
            "status",
            "created_at",
        ]
        # These fields are generated automatically
        read_only_fields = ["id", "tracking_number", "status", "created_at"]



    # Validate that sender and destination offices are different
    def validate(self, attrs):
        if attrs.get("sender_office") == attrs.get("destination_office"):
            raise serializers.ValidationError(
                {
                    "destination_office": "Sender and destination offices must be different."
                }
            )
        return attrs



    # Create parcel and first history record automatically
    def create(self, validated_data):
        parcel = super().create(validated_data)

        ParcelStatusHistory.objects.create(
            parcel=parcel,
            status=parcel.status,
            office=parcel.sender_office,
            comment="Parcel created",
        )

        return parcel




# Serializer for parcel status updates
class ParcelStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Parcel.Status.choices)
    office = serializers.PrimaryKeyRelatedField(queryset=PostOffice.objects.all())
    comment = serializers.CharField(required=False, allow_blank=True, max_length=255)




    # Business validation for status transitions
    def validate_status(self, new_status):
        parcel = self.context["parcel"]

        if parcel.status in Parcel.TERMINAL_STATUSES:
            raise serializers.ValidationError("Terminal statuses cannot be changed.")

        if new_status == parcel.status:
            raise serializers.ValidationError("Parcel already has this status.")

        has_arrived = (
            parcel.status == Parcel.Status.ARRIVED
            or parcel.history.filter(status=Parcel.Status.ARRIVED).exists()
        )

        if new_status == Parcel.Status.DELIVERED and not has_arrived:
            raise serializers.ValidationError(
                "Parcel cannot be delivered before it has arrived."
            )

        return new_status




    # Save new parcel status and create history record
    def save(self, **kwargs):
        parcel = self.context["parcel"]
        new_status = self.validated_data["status"]
        office = self.validated_data["office"]

        parcel.status = new_status
        parcel.save(update_fields=["status"])

        return ParcelStatusHistory.objects.create(
            parcel=parcel,
            status=new_status,
            office=office,
            comment=self.validated_data.get("comment", ""),
        )