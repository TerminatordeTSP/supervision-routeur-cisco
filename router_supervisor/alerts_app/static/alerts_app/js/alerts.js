/**
 * MODERN ALERTS DASHBOARD JAVASCRIPT
 * Système d'alertes pour supervision de routeurs
 */

class AlertsDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.initCountingNumbers();
        this.initRealTimeUpdates();
        this.initFilterActions();
        this.initAlertActions();
        this.initAutoRefresh();
        this.initTooltips();
    }

    /**
     * Animation des nombres qui comptent
     */
    initCountingNumbers() {
        const numbers = document.querySelectorAll('.stat-number');
        
        numbers.forEach(number => {
            const target = parseInt(number.textContent);
            if (isNaN(target)) return;
            
            number.textContent = '0';
            number.classList.add('counting-number');
            
            this.animateNumber(number, 0, target, 1500);
        });
    }

    animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function pour un effet plus naturel
            const eased = this.easeOutCubic(progress);
            const current = Math.round(start + (end - start) * eased);
            
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    /**
     * Mise à jour en temps réel des statistiques
     */
    initRealTimeUpdates() {
        // Mettre à jour les statistiques toutes les 30 secondes
        setInterval(() => {
            this.updateStats();
        }, 30000);
    }

    async updateStats() {
        try {
            const response = await fetch('/alerts/api/summary/');
            const data = await response.json();
            
            this.updateStatCard('total-alerts', data.total_active);
            this.updateStatCard('critical-alerts', data.by_severity.critical);
            this.updateStatCard('high-alerts', data.by_severity.high);
            this.updateStatCard('medium-alerts', data.by_severity.medium);
            
            // Afficher une notification discrète
            this.showNotification('Statistiques mises à jour', 'success');
            
        } catch (error) {
            console.error('Erreur lors de la mise à jour:', error);
            this.showNotification('Erreur de mise à jour', 'error');
        }
    }

    updateStatCard(id, newValue) {
        const element = document.getElementById(id);
        if (element) {
            const currentValue = parseInt(element.textContent.replace(/,/g, ''));
            if (currentValue !== newValue) {
                element.style.transform = 'scale(1.1)';
                element.style.transition = 'transform 0.3s ease';
                
                setTimeout(() => {
                    this.animateNumber(element, currentValue, newValue, 800);
                    element.style.transform = 'scale(1)';
                }, 100);
            }
        }
    }

    /**
     * Filtres et recherche
     */
    initFilterActions() {
        const searchInput = document.getElementById('search-alerts');
        const severityFilter = document.getElementById('severity-filter');
        const statusFilter = document.getElementById('status-filter');
        
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.filterAlerts();
                }, 300);
            });
        }
        
        if (severityFilter) {
            severityFilter.addEventListener('change', () => this.filterAlerts());
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterAlerts());
        }
    }

    filterAlerts() {
        const searchTerm = document.getElementById('search-alerts')?.value.toLowerCase() || '';
        const severityFilter = document.getElementById('severity-filter')?.value || '';
        const statusFilter = document.getElementById('status-filter')?.value || '';
        
        const alertCards = document.querySelectorAll('.alert-card');
        let visibleCount = 0;
        
        alertCards.forEach(card => {
            const title = card.querySelector('.alert-title')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.alert-description')?.textContent.toLowerCase() || '';
            const severity = card.classList.contains('critical') ? 'critical' :
                           card.classList.contains('high') ? 'high' :
                           card.classList.contains('medium') ? 'medium' : 'low';
            const status = card.querySelector('.status-active') ? 'active' :
                          card.querySelector('.status-acknowledged') ? 'acknowledged' :
                          card.querySelector('.status-resolved') ? 'resolved' : 'dismissed';
            
            const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
            const matchesSeverity = !severityFilter || severity === severityFilter;
            const matchesStatus = !statusFilter || status === statusFilter;
            
            if (matchesSearch && matchesSeverity && matchesStatus) {
                card.style.display = 'block';
                card.style.animation = 'slideInUp 0.4s ease-out';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Afficher le nombre de résultats
        this.updateResultsCount(visibleCount);
    }

    updateResultsCount(count) {
        let resultsDiv = document.getElementById('filter-results');
        if (!resultsDiv) {
            resultsDiv = document.createElement('div');
            resultsDiv.id = 'filter-results';
            resultsDiv.className = 'filter-results mt-2 text-muted';
            document.querySelector('.alerts-filters')?.appendChild(resultsDiv);
        }
        
        resultsDiv.textContent = `${count} alerte(s) trouvée(s)`;
    }

    /**
     * Actions sur les alertes
     */
    initAlertActions() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-acknowledge, .btn-resolve, .btn-dismiss')) {
                e.preventDefault();
                const action = e.target.classList.contains('btn-acknowledge') ? 'acknowledge' :
                              e.target.classList.contains('btn-resolve') ? 'resolve' : 'dismiss';
                
                const alertCard = e.target.closest('.alert-card');
                const alertId = alertCard?.dataset.alertId;
                
                if (alertId) {
                    this.performAlertAction(alertId, action, alertCard);
                }
            }
        });
    }

    async performAlertAction(alertId, action, alertCard) {
        try {
            // Désactiver le bouton pendant l'action
            const button = alertCard.querySelector(`.btn-${action}`);
            const originalText = button.textContent;
            button.textContent = 'Traitement...';
            button.disabled = true;
            
            const response = await fetch(`/alerts/alert/${alertId}/${action}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                // Animation de succès
                alertCard.style.transform = 'scale(0.95)';
                alertCard.style.opacity = '0.7';
                
                setTimeout(() => {
                    // Mettre à jour le statut de l'alerte
                    this.updateAlertStatus(alertCard, action);
                    alertCard.style.transform = 'scale(1)';
                    alertCard.style.opacity = '1';
                }, 300);
                
                this.showNotification(`Alerte ${action === 'acknowledge' ? 'acquittée' : action === 'resolve' ? 'résolue' : 'rejetée'}`, 'success');
                
                // Mettre à jour les statistiques
                setTimeout(() => this.updateStats(), 500);
                
            } else {
                throw new Error('Erreur lors de l\'action');
            }
            
        } catch (error) {
            console.error('Erreur:', error);
            this.showNotification('Erreur lors de l\'action', 'error');
            
            // Restaurer le bouton
            button.textContent = originalText;
            button.disabled = false;
        }
    }

    updateAlertStatus(alertCard, action) {
        // Supprimer les anciens badges de statut
        const oldStatusBadges = alertCard.querySelectorAll('.status-active, .status-acknowledged, .status-resolved, .status-dismissed');
        oldStatusBadges.forEach(badge => badge.remove());
        
        // Ajouter le nouveau badge
        const badgesContainer = alertCard.querySelector('.alert-badges');
        const newBadge = document.createElement('span');
        newBadge.className = `alert-badge status-${action}d`;
        newBadge.textContent = action === 'acknowledge' ? 'Acquittée' : 
                              action === 'resolve' ? 'Résolue' : 'Rejetée';
        badgesContainer.appendChild(newBadge);
        
        // Mettre à jour les actions disponibles
        this.updateAvailableActions(alertCard, action);
    }

    updateAvailableActions(alertCard, action) {
        const actionsContainer = alertCard.querySelector('.alert-actions');
        if (!actionsContainer) return;
        
        // Supprimer l'action qui vient d'être effectuée
        const actionButton = actionsContainer.querySelector(`.btn-${action}`);
        if (actionButton) {
            actionButton.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => actionButton.remove(), 300);
        }
    }

    /**
     * Actualisation automatique
     */
    initAutoRefresh() {
        let autoRefreshEnabled = localStorage.getItem('autoRefresh') === 'true';
        
        const toggleButton = document.getElementById('auto-refresh-toggle');
        if (toggleButton) {
            toggleButton.checked = autoRefreshEnabled;
            toggleButton.addEventListener('change', (e) => {
                autoRefreshEnabled = e.target.checked;
                localStorage.setItem('autoRefresh', autoRefreshEnabled);
                
                if (autoRefreshEnabled) {
                    this.startAutoRefresh();
                    this.showNotification('Actualisation automatique activée', 'info');
                } else {
                    this.stopAutoRefresh();
                    this.showNotification('Actualisation automatique désactivée', 'info');
                }
            });
        }
        
        if (autoRefreshEnabled) {
            this.startAutoRefresh();
        }
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // S'assurer qu'il n'y a pas de doublon
        
        this.autoRefreshInterval = setInterval(() => {
            this.updateStats();
            
            // Optionnel: recharger la page complète toutes les 5 minutes
            if (Date.now() - this.lastFullRefresh > 300000) {
                location.reload();
            }
        }, 10000); // Toutes les 10 secondes
        
        this.lastFullRefresh = Date.now();
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    /**
     * Tooltips et aide contextuelle
     */
    initTooltips() {
        const elementsWithTooltips = document.querySelectorAll('[data-tooltip]');
        
        elementsWithTooltips.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        this.hideTooltip(); // Supprimer l'ancien tooltip
        
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: #2c3e50;
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: 4px;
            font-size: 0.8rem;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            pointer-events: none;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        this.currentTooltip = tooltip;
    }

    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    /**
     * Notifications toast
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1001;
            transform: translateX(100%);
            transition: transform 0.3s ease-out;
            max-width: 300px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        `;
        
        // Couleurs selon le type
        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };
        
        notification.style.background = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animation d'entrée
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Suppression automatique
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Utilitaires
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    new AlertsDashboard();
});

// Export pour utilisation dans d'autres scripts
window.AlertsDashboard = AlertsDashboard;
