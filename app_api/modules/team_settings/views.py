import json

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from app_api.modules.team_settings.maker import SettingsMaker
from app_api.modules.team_settings.serializers import team_to_serializer_data
from app_prime_league.models import Team


class SettingsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, ):
        data = request.query_params
        maker = SettingsMaker(data=data)
        maker.enc_and_hash_are_valid(raise_exception=True)
        data = team_to_serializer_data(maker.team)
        return Response(data)

    def post(self, request, ):
        data = request.data
        maker = SettingsMaker(data=data)
        maker.validate_data(raise_exception=True)
        maker.save()
        data = team_to_serializer_data(maker.team)
        return Response(data)


@api_view(http_method_names=['GET'])
def create(request):
    data = request.query_params
    team_id = data.get("team_id", 105959)
    team = Team.objects.get(id=team_id)
    maker = SettingsMaker(team=team)
    data = {
        "url": maker.generate_expiring_link("discord")
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
