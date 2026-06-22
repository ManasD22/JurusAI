from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """Registration accepting a single 'full_name' (as in the Create Account UI).

    Username is optional and auto-derived from the email when not supplied.
    """

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "phone_number", "full_name")
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        username = (attrs.get("username") or "").strip()
        email = (attrs.get("email") or "").strip()

        if not email:
            raise serializers.ValidationError({"email": "Email is required."})

        if not username:
            base = email.split("@")[0] or "user"
            candidate = base
            suffix = 1
            while CustomUser.objects.filter(username=candidate).exists():
                suffix += 1
                candidate = f"{base}{suffix}"
            attrs["username"] = candidate

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "An account with this email already exists."})

        return attrs

    def create(self, validated_data):
        full_name = (validated_data.pop("full_name", "") or "").strip()
        first_name, _, last_name = full_name.partition(" ")

        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data.get("phone_number"),
        )
        if first_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=["first_name", "last_name"])
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "first_name", "last_name", "full_name", "is_staff")

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or obj.username
