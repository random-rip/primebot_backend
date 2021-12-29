# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from app_api.modules.team_settings.maker import SettingsMaker
from app_api.modules.team_settings.serializers import team_to_serializer_data


class SettingsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, ):
        data = request.query_params
        print(data)
        maker = SettingsMaker(data=data)
        maker.enc_and_hash_are_valid(raise_exception=True)
        data = team_to_serializer_data(maker.team)
        return Response(data)

    def post(self, request, ):
        data = request.data
        print(data)
        maker = SettingsMaker(data=data)
        maker.data_is_valid(raise_exception=True)
        data = team_to_serializer_data(maker.team)
        return Response(data)
