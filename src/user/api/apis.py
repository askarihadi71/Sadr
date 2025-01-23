from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from user.api.permisions import SuperUserPermission
from user.models import OTP, User, AppConfig
from user.senders import send_otp_email


class UsersSearchListAPIView(APIView):
    '''
        - search on users by username, first_name, last_name , phone or email
    '''
    permission_classes = (SuperUserPermission,)

    class UsersSearchSearializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['pk','username','first_name','last_name', 'email', 'phone']

    def get(self, request):
        users = User.objects.all()
        if 'search' in request.query_params:
            searchParam = request.query_params.get('search')
            users=users.filter(
                Q(first_name__icontains=searchParam) |
                Q(last_name__icontains=searchParam) |
                Q(phone__icontains=searchParam) |
                Q(email__icontains=searchParam)
            )
        serializer = self.UsersSearchSearializer(users[:10], many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)



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

        
class AppConfigAPIView(APIView):
    permission_classes = (IsAuthenticated,SuperUserPermission)
    
    
    class AppConfigSerializer(serializers.ModelSerializer):
        class Meta:
            model = AppConfig
            fields = ['sms_linenumber', 'otp_pattern', 'change_phone_pattern']
    
    
    def get_object(self):
        obj, _ = AppConfig.objects.get_or_create()
        return obj
    
    def get(self,request):
        config = self.get_object()
        serializer = self.AppConfigSerializer(config)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        config = self.get_object()
             
        serializer = self.AppConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        config.sms_linenumber=serializer.validated_data.get("sms_linenumber")
        config.otp_pattern=serializer.validated_data.get("otp_pattern")
        config.change_phone_pattern=serializer.validated_data.get("change_phone_pattern")
       

        config.full_clean()
        config.save()
        
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
