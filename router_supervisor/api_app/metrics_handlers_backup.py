import logging
from datetime import datetime
from router_supervisor.core_models.models import Router, Interface, KPI, KPI_Interface_Log
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

# Import du service d'alertes - temporairement désactivé
ALERTS_ENABLED = False

class MetricsProcessor:
    """
    Handler class to process and store metrics received from Telegraf
    """

    @staticmethod
    def process_metrics(metrics_data):
        """
        Process received metrics and store them in the database
        """
        try:
            # Process router-level metrics
            MetricsProcessor._process_router_metrics(metrics_data)
            
            # Process interface-level metrics
            if 'interfaces' in metrics_data:
                for interface_data in metrics_data['interfaces']:
                    MetricsProcessor._process_interface_metrics(interface_data, metrics_data.get('router'))
            
            logger.info(f"Successfully processed metrics for router: {metrics_data.get('router', 'unknown')}")
            
        except Exception as e:
            logger.exception(f"Error processing metrics: {str(e)}")
            raise

    @staticmethod
    def _process_router_metrics(metrics_data):
        """Process router-level metrics"""
        router_name = metrics_data.get('router')
        if not router_name:
            logger.warning("No router name provided in metrics")
            return
            
        try:
            router = Router.objects.get(name=router_name)
        except Router.DoesNotExist:
            # Create router if it doesn't exist
            try:
                with transaction.atomic():
                    router = Router.objects.create(
                        name=router_name,
                        description=f"Auto-created router for {router_name}",
                        location="Unknown"
                    )
                    logger.info(f"Created new router: {router_name}")
            except Exception as e:
                logger.warning(f"Could not find or create router: {router_name}")
                return
        
        # Process CPU metrics
        if 'cpu_usage' in metrics_data:
            MetricsProcessor._process_cpu_metric(
                router, metrics_data['cpu_usage'], metrics_data.get('timestamp')
            )
            
        # Process memory metrics
        if 'memory_usage' in metrics_data:
            MetricsProcessor._process_memory_metric(
                router, metrics_data['memory_usage'], metrics_data.get('timestamp')
            )

    @staticmethod
    def _process_interface_metrics(interface_data, router_name):
        """Process interface-level metrics"""
        if not router_name:
            logger.warning("No router name provided for interface metrics")
            return
            
        interface_name = interface_data.get('interface')
        if not interface_name:
            logger.warning("No interface name provided in interface metrics")
            return
            
        try:
            router = Router.objects.get(name=router_name)
        except Router.DoesNotExist:
            logger.warning(f"Router {router_name} not found in database")
            return
            
        # Process traffic metrics
        if 'traffic_in' in interface_data or 'traffic_out' in interface_data:
            MetricsProcessor._process_traffic_metric(
                router, interface_data, interface_data.get('timestamp')
            )

    @staticmethod
    def _process_cpu_metric(router, cpu_usage, timestamp_str):
        """Process CPU usage metric"""
        try:
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()
            
            # Get or create CPU KPI
            cpu_kpi, created = KPI.objects.get_or_create(name='CPU')
            
            # Check if threshold exists and is exceeded
            if hasattr(router, 'threshold') and router.threshold and router.threshold.cpu:
                if cpu_usage > router.threshold.cpu:
                    logger.warning(f"CPU threshold exceeded for {router.name}: {cpu_usage}% > {router.threshold.cpu}%")
            
            # For simplicity, we're logging to the first interface
            default_interface = MetricsProcessor._get_default_interface(router)
            
            # Create log entry
            log_id = int(timestamp.timestamp())
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                ID=log_id,
                defaults={
                    'router': router,
                    'interface': default_interface,
                    'KPI': cpu_kpi,
                    'value': cpu_usage,
                    'timestamp': timestamp
                }
            )
            
            if not created:
                log_entry.value = cpu_usage
                log_entry.timestamp = timestamp
                log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing CPU metric: {str(e)}")

    @staticmethod
    def _process_memory_metric(router, memory_usage, timestamp_str):
        """Process memory usage metric"""
        try:
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()
            
            # Get or create Memory KPI
            memory_kpi, created = KPI.objects.get_or_create(name='Memory')
            
            # Check if threshold exists and is exceeded
            if hasattr(router, 'threshold') and router.threshold and router.threshold.ram:
                if memory_usage > router.threshold.ram:
                    logger.warning(f"RAM threshold exceeded for {router.name}: {memory_usage}MB > {router.threshold.ram}MB")
            
            # For simplicity, we're logging to the first interface
            default_interface = MetricsProcessor._get_default_interface(router)
            
            # Create log entry
            log_id = int(timestamp.timestamp())
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                ID=log_id + 1,  # Offset to avoid conflicts with CPU
                defaults={
                    'router': router,
                    'interface': default_interface,
                    'KPI': memory_kpi,
                    'value': memory_usage,
                    'timestamp': timestamp
                }
            )
            
            if not created:
                log_entry.value = memory_usage
                log_entry.timestamp = timestamp
                log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing memory metric: {str(e)}")

    @staticmethod
    def _process_traffic_metric(router, interface_data, timestamp_str):
        """Process traffic metrics for an interface"""
        try:
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()
            
            interface_name = interface_data.get('interface')
            traffic_in = interface_data.get('traffic_in', 0)
            traffic_out = interface_data.get('traffic_out', 0)
            
            # Calculate total traffic in Mbps
            traffic_mbps = (traffic_in + traffic_out) / (1024 * 1024 * 8)  # Convert bytes to Mbps
            
            # Get or create interface
            interface = MetricsProcessor._get_or_create_interface(router, interface_name)
            
            # Get or create Traffic KPI
            traffic_kpi, created = KPI.objects.get_or_create(name='Traffic')
            
            # Check if threshold exists and is exceeded
            if hasattr(router, 'threshold') and router.threshold and router.threshold.traffic:
                if traffic_mbps > router.threshold.traffic:
                    logger.warning(f"Traffic threshold exceeded for {router.name}: {traffic_mbps}Mbps > {router.threshold.traffic}Mbps")
            
            # Create log entry
            log_id = int(timestamp.timestamp()) + hash(interface_name) % 1000
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                ID=log_id,
                defaults={
                    'router': router,
                    'interface': interface,
                    'KPI': traffic_kpi,
                    'value': traffic_mbps,
                    'timestamp': timestamp
                }
            )
            
            if not created:
                log_entry.value = traffic_mbps
                log_entry.timestamp = timestamp
                log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing traffic metric: {str(e)}")

    @staticmethod
    def _get_or_create_interface(router, interface_name):
        """Get or create an interface for the router"""
        try:
            interface = Interface.objects.get(
                router=router,
                name=interface_name
            )
        except Interface.DoesNotExist:
            # Create interface if it doesn't exist
            interface = Interface.objects.create(
                router=router,
                name=interface_name,
                description=f"Auto-created interface {interface_name}",
                type="ethernet"  # Default type
            )
            logger.info(f"Created new interface: {interface_name} for router {router.name}")
        except Interface.MultipleObjectsReturned:
            # If multiple interfaces exist, get the first one
            interface = Interface.objects.filter(
                router=router,
                name=interface_name
            ).first()
            logger.warning(f"Multiple interfaces found for {interface_name} on router {router.name}")
        
        return interface

    @staticmethod
    def _get_default_interface(router):
        """Get a default interface for the router"""
        try:
            # Try to get an existing interface
            interface = Interface.objects.filter(router=router).first()
            
            if not interface:
                # Create a default interface if none exists
                interface = Interface.objects.create(
                    router=router,
                    name="default",
                    description="Default interface for system metrics",
                    type="virtual"
                )
                logger.info(f"Created default interface for router {router.name}")
            
            return interface
            
        except Exception as e:
            logger.exception(f"Error getting default interface: {str(e)}")
            return None
