# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from app_prime_league.modules.team_settings import SettingsMaker


class SettingsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, ):
        data = request.query_params
        print(data)
        # maker = SettingsMaker(data=data)
        return Response("GET")

    def post(self, request, ):
        data = request.data
        print(data)
        # maker = SettingsMaker(data=data)
        return Response("POST")
