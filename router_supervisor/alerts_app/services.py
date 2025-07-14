import logging
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from typing import Optional, Dict, Any

from .models import Alert, AlertRule, AlertSeverity, AlertType, AlertStatus, AlertHistory
from router_supervisor.core_models.models import Router, Interface, KPI, Threshold

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service pour gérer la création et la gestion des alertes
    """
    
    @staticmethod
    def check_thresholds_and_create_alerts(router: Router, interface: Optional[Interface], 
                                          kpi: KPI, value: float, timestamp=None) -> Optional[Alert]:
        """
        Vérifier les seuils et créer une alerte si nécessaire
        
        Args:
            router: Instance du routeur
            interface: Instance de l'interface (optionnel)
            kpi: Instance du KPI
            value: Valeur actuelle de la métrique
            timestamp: Timestamp de la métrique
            
        Returns:
            Alert créée ou None
        """
        if timestamp is None:
            timestamp = timezone.now()
            
        try:
            with transaction.atomic():
                # Vérifier les règles personnalisées d'abord
                alert = AlertService._check_custom_rules(router, interface, kpi, value, timestamp)
                if alert:
                    return alert
                
                # Vérifier les seuils standard du routeur
                if router.threshold:
                    alert = AlertService._check_standard_thresholds(
                        router, interface, kpi, value, timestamp
                    )
                    if alert:
                        return alert
                
                return None
                
        except Exception as e:
            logger.exception(f"Erreur lors de la vérification des seuils: {str(e)}")
            return None
    
    @staticmethod
    def _check_custom_rules(router: Router, interface: Optional[Interface], 
                           kpi: KPI, value: float, timestamp) -> Optional[Alert]:
        """Vérifier les règles personnalisées d'alertes"""
        
        # Récupérer les règles applicables
        rules = AlertRule.objects.filter(
            kpi=kpi,
            is_active=True
        )
        
        # Filtrer par routeur si spécifié dans la règle
        applicable_rules = []
        for rule in rules:
            if rule.router and rule.router != router:
                continue
            if rule.interface and rule.interface != interface:
                continue
            applicable_rules.append(rule)
        
        # Vérifier chaque règle
        for rule in applicable_rules:
            if rule.check_condition(value):
                # Vérifier le cooldown
                if rule.should_trigger_alert(router, interface):
                    return AlertService._create_alert_from_rule(
                        rule, router, interface, kpi, value, timestamp
                    )
        
        return None
    
    @staticmethod
    def _check_standard_thresholds(router: Router, interface: Optional[Interface],
                                  kpi: KPI, value: float, timestamp) -> Optional[Alert]:
        """Vérifier les seuils standard du routeur"""
        
        threshold = router.threshold
        threshold_value = None
        unit = ""
        
        # Déterminer le seuil selon le KPI
        if kpi.name.upper() in ['CPU', 'CPU_USAGE']:
            threshold_value = threshold.cpu
            unit = "%"
        elif kpi.name.upper() in ['RAM', 'MEMORY', 'MEMORY_USAGE']:
            threshold_value = threshold.ram
            unit = "MB"
        elif kpi.name.upper() in ['TRAFFIC', 'TRAFFIC_MBPS', 'INTERFACE_TRAFFIC']:
            threshold_value = threshold.traffic
            unit = "Mbps"
        
        if threshold_value is None:
            return None
        
        # Vérifier si le seuil est dépassé
        if value > threshold_value:
            # Vérifier s'il existe déjà une alerte similaire récente
            if not AlertService._should_create_duplicate_alert(router, interface, kpi):
                return None
                
            return AlertService._create_threshold_alert(
                router, interface, kpi, value, threshold_value, unit, timestamp
            )
        
        return None
    
    @staticmethod
    def _should_create_duplicate_alert(router: Router, interface: Optional[Interface], 
                                     kpi: KPI, cooldown_minutes: int = 5) -> bool:
        """Vérifier s'il faut créer une alerte dupliquée"""
        
        cooldown_time = timezone.now() - timezone.timedelta(minutes=cooldown_minutes)
        
        existing_alerts = Alert.objects.filter(
            router=router,
            kpi=kpi,
            status=AlertStatus.ACTIVE,
            created_at__gte=cooldown_time
        )
        
        if interface:
            existing_alerts = existing_alerts.filter(interface=interface)
        
        return not existing_alerts.exists()
    
    @staticmethod
    def _create_threshold_alert(router: Router, interface: Optional[Interface], 
                               kpi: KPI, current_value: float, threshold_value: float,
                               unit: str, timestamp) -> Alert:
        """Créer une alerte de dépassement de seuil"""
        
        # Déterminer la sévérité selon le dépassement
        percentage_over = ((current_value - threshold_value) / threshold_value) * 100
        
        if percentage_over >= 100:  # Plus de 100% au-dessus du seuil
            severity = AlertSeverity.CRITICAL
        elif percentage_over >= 50:  # 50-100% au-dessus
            severity = AlertSeverity.HIGH
        elif percentage_over >= 20:  # 20-50% au-dessus
            severity = AlertSeverity.MEDIUM
        else:  # Moins de 20% au-dessus
            severity = AlertSeverity.LOW
        
        # Créer le titre et la description
        interface_name = interface.name if interface else "Global"
        title = f"Seuil {kpi.name} dépassé sur {router.name}"
        if interface:
            title += f" ({interface_name})"
        
        description = (
            f"Le seuil de {kpi.name} a été dépassé sur le routeur {router.name}.\n"
            f"Valeur actuelle: {current_value:.2f} {unit}\n"
            f"Seuil configuré: {threshold_value:.2f} {unit}\n"
            f"Dépassement: +{percentage_over:.1f}%"
        )
        
        if interface:
            description += f"\nInterface: {interface_name}"
        
        # Créer l'alerte
        alert = Alert.objects.create(
            router=router,
            interface=interface,
            threshold=router.threshold,
            kpi=kpi,
            alert_type=AlertType.THRESHOLD,
            severity=severity,
            title=title,
            description=description,
            metric_name=kpi.name,
            current_value=Decimal(str(current_value)),
            threshold_value=Decimal(str(threshold_value)),
            unit=unit,
            created_at=timestamp,
            additional_data={
                'percentage_over_threshold': percentage_over,
                'router_name': router.name,
                'interface_name': interface_name if interface else None,
            }
        )
        
        # Logger l'alerte
        logger.warning(
            f"ALERTE CRÉÉE: {title} - "
            f"Valeur: {current_value:.2f}{unit} > Seuil: {threshold_value:.2f}{unit}"
        )
        
        return alert
    
    @staticmethod
    def _create_alert_from_rule(rule: AlertRule, router: Router, interface: Optional[Interface],
                               kpi: KPI, value: float, timestamp) -> Alert:
        """Créer une alerte basée sur une règle personnalisée"""
        
        interface_name = interface.name if interface else "Global"
        title = f"Règle '{rule.name}' déclenchée sur {router.name}"
        if interface:
            title += f" ({interface_name})"
        
        description = (
            f"La règle d'alerte '{rule.name}' a été déclenchée.\n"
            f"Condition: {kpi.name} {rule.get_operator_display()} {rule.threshold_value}\n"
            f"Valeur actuelle: {value}\n"
            f"Description de la règle: {rule.description}"
        )
        
        if interface:
            description += f"\nInterface: {interface_name}"
        
        alert = Alert.objects.create(
            router=router,
            interface=interface,
            kpi=kpi,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=title,
            description=description,
            metric_name=kpi.name,
            current_value=Decimal(str(value)),
            threshold_value=rule.threshold_value,
            created_at=timestamp,
            additional_data={
                'rule_id': rule.id,
                'rule_name': rule.name,
                'router_name': router.name,
                'interface_name': interface_name if interface else None,
            }
        )
        
        logger.warning(
            f"ALERTE RÈGLE CRÉÉE: {title} - "
            f"Règle: {rule.name}, Valeur: {value}"
        )
        
        return alert
    
    @staticmethod
    def acknowledge_alert(alert_id: int, user_email: str = None, comment: str = "") -> bool:
        """Acquitter une alerte"""
        try:
            alert = Alert.objects.get(alert_id=alert_id)
            previous_status = alert.status
            
            alert.acknowledge()
            
            # Créer un historique
            AlertHistory.objects.create(
                alert=alert,
                previous_status=previous_status,
                new_status=alert.status,
                changed_by=user_email or "system",
                comment=comment
            )
            
            logger.info(f"Alerte {alert_id} acquittée par {user_email or 'system'}")
            return True
            
        except Alert.DoesNotExist:
            logger.error(f"Alerte {alert_id} non trouvée")
            return False
        except Exception as e:
            logger.exception(f"Erreur lors de l'acquittement de l'alerte {alert_id}: {str(e)}")
            return False
    
    @staticmethod
    def resolve_alert(alert_id: int, user_email: str = None, comment: str = "") -> bool:
        """Résoudre une alerte"""
        try:
            alert = Alert.objects.get(alert_id=alert_id)
            previous_status = alert.status
            
            alert.resolve()
            
            # Créer un historique
            AlertHistory.objects.create(
                alert=alert,
                previous_status=previous_status,
                new_status=alert.status,
                changed_by=user_email or "system",
                comment=comment
            )
            
            logger.info(f"Alerte {alert_id} résolue par {user_email or 'system'}")
            return True
            
        except Alert.DoesNotExist:
            logger.error(f"Alerte {alert_id} non trouvée")
            return False
        except Exception as e:
            logger.exception(f"Erreur lors de la résolution de l'alerte {alert_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_active_alerts_summary() -> Dict[str, Any]:
        """Obtenir un résumé des alertes actives"""
        try:
            active_alerts = Alert.objects.filter(status=AlertStatus.ACTIVE)
            
            summary = {
                'total_active': active_alerts.count(),
                'by_severity': {
                    'critical': active_alerts.filter(severity=AlertSeverity.CRITICAL).count(),
                    'high': active_alerts.filter(severity=AlertSeverity.HIGH).count(),
                    'medium': active_alerts.filter(severity=AlertSeverity.MEDIUM).count(),
                    'low': active_alerts.filter(severity=AlertSeverity.LOW).count(),
                },
                'by_type': {
                    'threshold': active_alerts.filter(alert_type=AlertType.THRESHOLD).count(),
                    'interface_down': active_alerts.filter(alert_type=AlertType.INTERFACE_DOWN).count(),
                    'high_error_rate': active_alerts.filter(alert_type=AlertType.HIGH_ERROR_RATE).count(),
                    'connectivity': active_alerts.filter(alert_type=AlertType.CONNECTIVITY).count(),
                },
                'recent_alerts': list(active_alerts.order_by('-created_at')[:5].values(
                    'alert_id', 'title', 'severity', 'created_at', 'router__name'
                ))
            }
            
            return summary
            
        except Exception as e:
            logger.exception(f"Erreur lors du calcul du résumé des alertes: {str(e)}")
            return {
                'total_active': 0,
                'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'by_type': {'threshold': 0, 'interface_down': 0, 'high_error_rate': 0, 'connectivity': 0},
                'recent_alerts': []
            }
    
    @staticmethod
    def auto_resolve_alerts_on_normal_values(router: Router, interface: Optional[Interface],
                                           kpi: KPI, value: float) -> int:
        """Résoudre automatiquement les alertes quand les valeurs redeviennent normales"""
        resolved_count = 0
        
        try:
            # Récupérer les alertes actives pour ce routeur/interface/kpi
            active_alerts = Alert.objects.filter(
                router=router,
                kpi=kpi,
                status=AlertStatus.ACTIVE,
                alert_type=AlertType.THRESHOLD
            )
            
            if interface:
                active_alerts = active_alerts.filter(interface=interface)
            
            for alert in active_alerts:
                # Vérifier si la valeur est maintenant sous le seuil
                if alert.threshold_value and value <= float(alert.threshold_value):
                    # Résoudre automatiquement l'alerte
                    previous_status = alert.status
                    alert.resolve()
                    
                    # Créer un historique
                    AlertHistory.objects.create(
                        alert=alert,
                        previous_status=previous_status,
                        new_status=alert.status,
                        changed_by="system",
                        comment=f"Résolution automatique - valeur retournée à la normale: {value}"
                    )
                    
                    resolved_count += 1
                    logger.info(
                        f"Alerte {alert.alert_id} résolue automatiquement - "
                        f"valeur: {value} <= seuil: {alert.threshold_value}"
                    )
            
        except Exception as e:
            logger.exception(f"Erreur lors de la résolution automatique: {str(e)}")
        
        return resolved_count
