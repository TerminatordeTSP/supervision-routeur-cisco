from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
import time
from .metrics_handlers import MetricsProcessor

# Configure logging
logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def receive_metrics(request):
    """
    API endpoint to receive metrics from Telegraf
    """
    # Log the raw request data
    logger.info(f"Received request from: {request.META.get('REMOTE_ADDR')}")
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Raw request body: {request.body.decode('utf-8', errors='replace')}")
    
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        
        # Log the received data for debugging
        logger.info(f"Parsed JSON data: {data}")
        logger.info(f"Data type: {type(data)}")
        
        # Process the metrics
        process_metrics(data)
        
        return JsonResponse({"status": "success", "message": "Metrics received"})
    
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON received: {str(e)}"
        logger.error(error_msg)
        return JsonResponse({"status": "error", "message": error_msg}, status=400)
    
    except Exception as e:
        logger.exception(f"Error processing metrics: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def process_metrics(data):
    """
    Process the received metrics data
    """
    # Example implementation to process metrics
    # This would depend on your specific requirements
    
    logger.info(f"Processing metrics data of type: {type(data)}")
    
    if isinstance(data, list):
        # Handle list of metrics
        logger.info(f"Processing metrics as list with {len(data)} items")
        for item in data:
            process_single_metric(item)
    elif isinstance(data, dict):
        # Check if it's a Telegraf format with 'metrics' key
        if 'metrics' in data:
            logger.info("Processing data with 'metrics' key")
            metrics = data.get('metrics', [])
            if isinstance(metrics, list):
                for item in metrics:
                    process_single_metric(item)
            else:
                process_single_metric(metrics)
        else:
            # Handle single metric
            logger.info("Processing single metric item")
            process_single_metric(data)
    else:
        logger.warning(f"Unexpected data format: {type(data)}")

def process_single_metric(metric):
    """
    Process a single metric entry
    """
    # Log the metric we're processing
    logger.info(f"Processing single metric: {metric}")
    
    try:
        # Handle Telegraf-specific format
        if 'fields' in metric and 'name' in metric:
            logger.info(f"Processing Telegraf native format metric: {metric['name']}")
            # Extract fields from Telegraf format
            fields = metric.get('fields', {})
            tags = metric.get('tags', {})
            
            # Create a more generic format that our processor can handle
            if 'router' in tags:
                router_name = tags.get('router')
                router_metrics = {
                    'cpu_usage': fields.get('cpu_usage', 0),
                    'memory_usage': fields.get('memory_usage', 0),
                    'traffic_mbps': fields.get('traffic_mbps', 0),
                }
                
                # Log the transformed data
                logger.info(f"Transformed Telegraf data: {router_name} - {router_metrics}")
                
                # Process with our metrics processor
                processed_metric = {
                    'router_name': router_name,
                    'router_metrics': router_metrics,
                    'timestamp': metric.get('timestamp', str(int(time.time())))
                }
                
                MetricsProcessor.process_router_metrics(processed_metric)
                return
        
        # Standard format processing
        # Extract router name if available
        router_name = metric.get('router_name', 'unknown')
        
        # Example processing for different metric types
        if 'router_metrics' in metric:
            # Use the metrics processor to handle router metrics
            success = MetricsProcessor.process_router_metrics(metric)
            
            if success:
                router_metrics = metric['router_metrics']
                cpu_usage = router_metrics.get('cpu_usage')
                memory_usage = router_metrics.get('memory_usage')
                traffic = router_metrics.get('traffic_mbps')
                
                logger.info(f"Router {router_name}: CPU: {cpu_usage}%, Memory: {memory_usage}%, Traffic: {traffic} Mbps")
            else:
                logger.warning(f"Failed to process metrics for router: {router_name}")
        
        # Handle simulated metrics from exec input plugin
        elif 'simulated_router_metrics' in metric:
            logger.info(f"Received simulated metrics: {metric}")
            # Extract fields from the simulated_router_metrics
            if isinstance(metric['simulated_router_metrics'], str):
                # Try to parse it as JSON if it's a string
                try:
                    router_data = json.loads(metric['simulated_router_metrics'])
                    MetricsProcessor.process_router_metrics(router_data)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse simulated metrics: {metric['simulated_router_metrics']}")
            else:
                logger.info(f"Using simulated metrics directly")
                MetricsProcessor.process_router_metrics(metric)
        else:
            logger.warning(f"Unknown metric format: {metric}")
            
    except Exception as e:
        logger.exception(f"Error processing single metric: {str(e)}")