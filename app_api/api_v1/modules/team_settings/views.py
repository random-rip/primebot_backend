from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from app_api.api_v1.modules.team_settings.serializers import team_to_serializer_data
from core.settings_maker import SettingsMaker


@extend_schema(exclude=True)
class SettingsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        data = request.query_params
        maker = SettingsMaker(data=data)
        maker.enc_and_hash_are_valid(raise_exception=True)
        data = team_to_serializer_data(maker.team)
        return Response(data)

    def post(self, request):
        data = request.data
        maker = SettingsMaker(data=data)
        maker.validate_data(raise_exception=True)
        maker.save()
        data = team_to_serializer_data(maker.team)
        return Response(data)
