import logging
from datetime import datetime
from router_supervisor.core_models.models import Router, Interface, KPI, KPI_Interface_Log
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

class MetricsProcessor:
    """
    Handler class to process and store metrics received from Telegraf
    """
    
    @staticmethod
    def process_router_metrics(data):
        """
        Process metrics related to routers
        
        Args:
            data (dict): The metrics data from Telegraf
        """
        try:
            router_name = data.get('router_name', 'unknown')
            timestamp = data.get('timestamp')
            metrics = data.get('router_metrics', {})
            
            # Convert timestamp to datetime if provided as Unix timestamp
            if timestamp and isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromtimestamp(int(timestamp))
                except ValueError:
                    timestamp = timezone.now()
            else:
                timestamp = timezone.now()
            
            with transaction.atomic():
                # Get or create router
                router = MetricsProcessor._get_or_create_router(router_name)
                
                if not router:
                    logger.warning(f"Could not find or create router: {router_name}")
                    return False
                
                # Process CPU metrics
                cpu_usage = metrics.get('cpu_usage')
                if cpu_usage is not None:
                    MetricsProcessor._process_cpu_metric(router, cpu_usage, timestamp)
                
                # Process memory metrics
                memory_usage = metrics.get('memory_usage')
                if memory_usage is not None:
                    MetricsProcessor._process_memory_metric(router, memory_usage, timestamp)
                
                # Process traffic metrics
                traffic_mbps = metrics.get('traffic_mbps')
                if traffic_mbps is not None:
                    MetricsProcessor._process_traffic_metric(router, traffic_mbps, timestamp)
                
                # Process interface metrics
                interfaces = metrics.get('interfaces', [])
                if interfaces:
                    for interface_data in interfaces:
                        MetricsProcessor._process_interface_metric(router, interface_data, timestamp)
                
            return True
            
        except Exception as e:
            logger.exception(f"Error processing router metrics: {str(e)}")
            return False
    
    @staticmethod
    def _get_or_create_router(router_name):
        """Get or create a router instance"""
        try:
            return Router.objects.get(name=router_name)
        except Router.DoesNotExist:
            logger.warning(f"Router {router_name} not found in database")
            # We don't create router automatically as it should have threshold configured
            return None
    
    @staticmethod
    def _get_or_create_kpi(kpi_name):
        """Get or create a KPI instance"""
        kpi, created = KPI.objects.get_or_create(name=kpi_name)
        return kpi
    
    @staticmethod
    def _get_or_create_interface(router, interface_name, initial_traffic=0):
        """Get or create an interface instance"""
        try:
            return Interface.objects.get(router=router, name=interface_name)
        except Interface.DoesNotExist:
            # Create new interface with default traffic
            interface = Interface(
                router=router,
                name=interface_name,
                traffic=initial_traffic
            )
            interface.save()
            return interface
        except Interface.MultipleObjectsReturned:
            # If multiple exist, return the first one
            logger.warning(f"Multiple interfaces found for {interface_name} on router {router.name}")
            return Interface.objects.filter(router=router, name=interface_name).first()
    
    @staticmethod
    def _process_cpu_metric(router, cpu_usage, timestamp):
        """Process CPU metrics"""
        try:
            kpi = MetricsProcessor._get_or_create_kpi("CPU")
            
            # Check threshold
            if router.threshold and cpu_usage > router.threshold.cpu:
                logger.warning(f"CPU threshold exceeded for {router.name}: {cpu_usage}% > {router.threshold.cpu}%")
                # Here you would trigger alerts
            
            # For simplicity, we're logging to the first interface
            # In a real implementation, you would handle CPU metrics differently
            default_interface = MetricsProcessor._get_default_interface(router)
            
            # Create log entry
            log_id = int(timestamp.timestamp())
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                interface=default_interface,
                log_id=log_id,
                kpi=kpi,
                defaults={'value': cpu_usage}
            )
            
            if not created:
                log_entry.value = cpu_usage
                log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing CPU metric: {str(e)}")
    
    @staticmethod
    def _process_memory_metric(router, memory_usage, timestamp):
        """Process memory metrics"""
        try:
            kpi = MetricsProcessor._get_or_create_kpi("RAM")
            
            # Check threshold
            if router.threshold and memory_usage > router.threshold.ram:
                logger.warning(f"RAM threshold exceeded for {router.name}: {memory_usage}MB > {router.threshold.ram}MB")
                # Here you would trigger alerts
            
            # For simplicity, we're logging to the first interface
            default_interface = MetricsProcessor._get_default_interface(router)
            
            # Create log entry
            log_id = int(timestamp.timestamp())
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                interface=default_interface,
                log_id=log_id,
                kpi=kpi,
                defaults={'value': memory_usage}
            )
            
            if not created:
                log_entry.value = memory_usage
                log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing memory metric: {str(e)}")
    
    @staticmethod
    def _process_traffic_metric(router, traffic_mbps, timestamp):
        """Process traffic metrics"""
        try:
            kpi = MetricsProcessor._get_or_create_kpi("Traffic")
            
            # Check threshold
            if router.threshold and traffic_mbps > router.threshold.traffic:
                logger.warning(f"Traffic threshold exceeded for {router.name}: {traffic_mbps}Mbps > {router.threshold.traffic}Mbps")
                # Here you would trigger alerts
            
            # For simplicity, we're logging to the first interface
            default_interface = MetricsProcessor._get_default_interface(router)
            
            # Update interface traffic
            default_interface.traffic = traffic_mbps
            default_interface.save()
            
            # Create log entry
            log_id = int(timestamp.timestamp())
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                interface=default_interface,
                log_id=log_id,
                kpi=kpi,
                defaults={'value': traffic_mbps}
            )
            
            if not created:
                log_entry.value = traffic_mbps
                log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing traffic metric: {str(e)}")
    
    @staticmethod
    def _process_interface_metric(router, interface_data, timestamp):
        """Process interface-specific metrics"""
        try:
            interface_name = interface_data.get('name', 'unknown')
            status = interface_data.get('status')
            input_rate = interface_data.get('input_rate', 0)
            output_rate = interface_data.get('output_rate', 0)
            errors = interface_data.get('errors', 0)
            
            # Calculate total traffic
            total_traffic = input_rate + output_rate
            
            # Get or create the interface
            interface = MetricsProcessor._get_or_create_interface(
                router, 
                interface_name, 
                initial_traffic=total_traffic
            )
            
            # Update interface traffic
            interface.traffic = total_traffic
            interface.save()
            
            # Process interface traffic
            kpi = MetricsProcessor._get_or_create_kpi("Interface Traffic")
            
            # Check threshold for interface traffic
            if router.threshold and total_traffic > router.threshold.traffic:
                logger.warning(
                    f"Interface {interface_name} traffic threshold exceeded for {router.name}: "
                    f"{total_traffic}Mbps > {router.threshold.traffic}Mbps"
                )
                # Here you would trigger alerts
            
            # Create log entry
            log_id = int(timestamp.timestamp())
            log_entry, created = KPI_Interface_Log.objects.get_or_create(
                interface=interface,
                log_id=log_id,
                kpi=kpi,
                defaults={'value': total_traffic}
            )
            
            if not created:
                log_entry.value = total_traffic
                log_entry.save()
                
            # Process error metrics if present
            if errors > 0:
                error_kpi = MetricsProcessor._get_or_create_kpi("Interface Errors")
                error_log_entry, created = KPI_Interface_Log.objects.get_or_create(
                    interface=interface,
                    log_id=log_id,
                    kpi=error_kpi,
                    defaults={'value': errors}
                )
                
                if not created:
                    error_log_entry.value = errors
                    error_log_entry.save()
                
        except Exception as e:
            logger.exception(f"Error processing interface metric: {str(e)}")
    
    @staticmethod
    def _get_default_interface(router):
        """Get or create a default interface for a router"""
        try:
            # Try to get an existing interface
            return Interface.objects.filter(router=router).first() or \
                   MetricsProcessor._get_or_create_interface(router, "default")
        except Exception as e:
            logger.exception(f"Error getting default interface: {str(e)}")
            # Create a new default interface
            return MetricsProcessor._get_or_create_interface(router, "default")