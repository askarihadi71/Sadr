from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from user.models import User
from user.senders import send_otp_email


class GetProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    class GetProfileOutputSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = [
                'first_name', 'last_name', 'email', 'phone',
            ]

    def get(self, request):
        user = request.user
        serialized_data = self.GetProfileOutputSerializer(instance=user)
        return Response(data=serialized_data.data)


class UpdateProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    class UpdateProfileInputSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [
                'first_name', 'last_name', 'phone'
                ]

    def post(self, request):
        serializer = self.UpdateProfileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.first_name = serializer.validated_data.get('first_name')
        user.last_name = serializer.validated_data.get('last_name')
        user.phone = serializer.validated_data.get('phone')

        user.full_clean()
        user.save()

        return Response({
            'status': status.HTTP_201_CREATED,
        })


class RequestEmailOTP(APIView):
    permission_classes =()
    def post(self, request):
        if not request.user.is_authenticated:
            token=request.session.get("otp_token")
            if token != None:
                otp = OTP.objects.filter(token=token)
                if otp.exists():
                    user = otp.first().user
                    send_otp_email.delay(user.pk)
        return Response(data={"message": "در صورتی که آدرس ایمیل تایید شده وجود داشته باشد کد ورود ارسال خواهد شد."},status=status.HTTP_200_OK)
