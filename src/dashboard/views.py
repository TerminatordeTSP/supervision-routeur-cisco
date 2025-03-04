from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'dashboard.html')

@csrf_exempt
def receive_telegraf_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received data: {data}")
            print(data)
            return JsonResponse({'status': 'success', 'data': data}, status=204)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    logger.warning(f"Invalid request method: {request.method}")
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# Create your views here.
