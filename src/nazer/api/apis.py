from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from nazer.api.permissions import DeviceDataPermission
from nazer.models import Alarm, Device, Alarm_Email, Alarm_SMS
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from user.api.permisions import SuperUserPermission
import logging

logger = logging.getLogger("db")
sp_logger = logging.getLogger("sp_db")


class Overview(APIView):
    permission_classes = (SuperUserPermission,)

    def get(self,request):
        data={
            'un_handled': Alarm.objects.filter(handled=False).count(),
            'all': Alarm.objects.all().count(),
            'all_emails': Alarm_Email.objects.all().count(),
            'all_sms': Alarm_SMS.objects.all().count(),
        }
        return Response(data=data, status=status.HTTP_200_OK)


class AlarmsList(APIView):
    permission_classes = (IsAuthenticated,)

    class AlarmsListOutputSerializer(serializers.ModelSerializer):
        device = serializers.SerializerMethodField("get_device")
        jTime = serializers.SerializerMethodField("get_jTime")


        def get_jTime(self, instance):
            return instance.jTime()
        
        def get_device(self, instance):
            return{
                'title': instance.device.title,
                'user': {
                    'name': instance.device.user.get_full_name(),
                    'phone': instance.device.user.phone,
                    'address': instance.device.user.address,
                } if instance.device.user else None
            }

        class Meta:
            model = Alarm
            fields = ('pk','alarm_type', 'time','is_sms_sent','is_email_sent','handled', 'device', 'device_name', 'alarm_name', 'jTime')

    def get(self, request):
        alarms = Alarm.objects.all().select_related("device", "device__user").order_by("-handled", "time")[:20]
        if not request.user.is_superuser:
            alarms = alarms.filter(device__user=request.user)
        serializer = self.AlarmsListOutputSerializer(alarms, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AlarmDetails(APIView):
    permission_classes = (DeviceDataPermission,)

    class AlarmOutputSerializer(serializers.ModelSerializer):
        file = serializers.SerializerMethodField("get_images")
        device = serializers.SerializerMethodField("get_device")
        jTime = serializers.SerializerMethodField("get_jTime")


        def get_jTime(self, instance):
            return instance.jTime()

        def __init__(self, *args, **kwargs):  
            context = kwargs.pop('context', None)  
            self.request= context.get('request', None)  
            super().__init__(*args, **kwargs)
        
        def get_images(self, instance):
            if instance.file:
                return{
                    'file': instance.file.url,
                }
            else: 
                return{
                    'file': None
                }
        
        def get_device(self, instance):
            return{
                'title': instance.device.title,
                'address': instance.device.address,
                'user': {
                    'name': instance.device.user.get_full_name(),
                    'phone': instance.device.user.phone,
                    'address': instance.device.user.address,
                } if instance.device.user else None
            }

        class Meta:
            model = Alarm
            fields = '__all__'

    def get(self, request, pk):
        user = request.user
        try:
            alarm = Alarm.objects.get(pk=pk)
        except Alarm.DoesNotExist:
            return Response(data={'error': 'User not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request=request, obj=alarm.device)
        serializer = self.AlarmOutputSerializer(alarm, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AlarmStatusChange(APIView):
    permission_classes = (DeviceDataPermission,)
    def get(self,request,pk):
        try:
            alarm = Alarm.objects.get(pk=pk)
        except Alarm.DoesNotExist:
            return Response(data={'error': 'Alarm not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request=request, obj=alarm.device)
        
        isHandled = alarm.handled 
        alarm.handled = not isHandled
        alarm.save()

        return Response(status=status.HTTP_200_OK)


class SetOwnerAPIView(APIView):
    permission_classes = (IsAuthenticated, SuperUserPermission)

    class SetOwnerInputSerializer(serializers.Serializer):
        device = serializers.IntegerField()
        user = serializers.IntegerField()

    def post(self, request):
        serializer = self.SetOwnerInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            device = Device.objects.get(pk=serializer.validated_data.get("device"))
        except Device.DoesNotExist:
            return Response(data={'error': 'Device not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = get_user_model().objects.get(pk=serializer.validated_data.get("user"))
        except get_user_model().DoesNotExist:
            return Response(data={'error': 'User not found!'},
                                status=status.HTTP_400_BAD_REQUEST)

        device.user = user
        device.save()
        data={
            'username': f'{user.get_full_name()} - {user.phone}',
            'name': f'{user.first_name} {user.last_name}',
            'pk': user.pk
        }
        sp_logger.info({'title':'SetOwnerAPIView','user':request.user.username,'device':serializer.validated_data.get("device"), 'newOwner':user.username})
        return Response(data=data,status=status.HTTP_200_OK)



class ClearOwnerAPIView(APIView):
    permission_classes = (IsAuthenticated, SuperUserPermission)

    class ClearOwnerInputSerializer(serializers.Serializer):
        device = serializers.IntegerField()

    def post(self, request):
        serializer = self.ClearOwnerInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            device = Device.objects.get(pk=serializer.validated_data.get("device"))
        except Device.DoesNotExist:
            return Response(data={'error': 'Device not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
        
        device.user = None
        device.save()

        sp_logger.info({'title':'ClearOwnerAPIView','user':request.user.username,'device':serializer.validated_data.get("device")})

        return Response(status=status.HTTP_200_OK)


from nazer.tasks import get_emails, process_emails
class Test(APIView):

    def get(self,request):
        process_emails.delay()
        return Response(status=status.HTTP_200_OK)