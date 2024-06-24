from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RateSerializer
from .services import get_all_rates, get_rate


class GetAllRates(APIView):
    def get(self, request):
        try:
            return Response(RateSerializer(get_all_rates(), many=True).data, status=200)
        except Exception as ex:
            return Response({'message': f'Error! {str(ex)}'}, status=400)


class GetRate(APIView):
    def get(self, request):
        try:
            rate_id = request.data['id']
            return Response(RateSerializer(get_rate(rate_id=rate_id)).data, status=200)
        except Exception as ex:
            return Response({'message': f'Error! {str(ex)}'}, status=400)
