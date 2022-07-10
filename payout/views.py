from rest_framework.response import Response
from rest_framework.decorators import api_view

from .payout import getCharges

# Create your views here.

@api_view(["GET"])
def payoutTest(request,amount):
    data = getCharges(amount)
    return Response(data)