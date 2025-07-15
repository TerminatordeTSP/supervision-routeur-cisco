# Script PowerShell pour redémarrer les services de supervision
# Utilisation: .\restart_services.ps1

Write-Host "🔄 Redémarrage des services de supervision..." -ForegroundColor Yellow

# Arrêter les conteneurs
Write-Host "⏹️  Arrêt des conteneurs..." -ForegroundColor Blue
docker-compose down

# Nettoyer les images si nécessaire
Write-Host "🧹 Nettoyage des images..." -ForegroundColor Blue
docker system prune -f

# Reconstruire les images
Write-Host "🔨 Reconstruction des images..." -ForegroundColor Blue
docker-compose build --no-cache

# Redémarrer les services
Write-Host "▶️  Redémarrage des services..." -ForegroundColor Blue
docker-compose up -d

# Attendre que les services soient prêts
Write-Host "⏳ Attente que les services soient prêts..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Vérifier le statut
Write-Host "📊 Vérification du statut..." -ForegroundColor Blue
docker-compose ps

# Afficher les logs récents
Write-Host "📋 Logs récents de Telegraf:" -ForegroundColor Green
docker logs telegraf --tail 20

Write-Host "📋 Logs récents de Django:" -ForegroundColor Green
docker logs router_django --tail 10

Write-Host "✅ Services redémarrés avec succès!" -ForegroundColor Green
Write-Host "🌐 Dashboard disponible sur: http://localhost:8080/" -ForegroundColor Cyan
Write-Host "📊 InfluxDB disponible sur: http://localhost:8086/" -ForegroundColor Cyan
Write-Host "🔧 pgAdmin disponible sur: http://localhost:5050/" -ForegroundColor Cyan

# Optionnel: Ouvrir le dashboard dans le navigateur
$response = Read-Host "Voulez-vous ouvrir le dashboard dans le navigateur? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Start-Process "http://localhost:8080/"
}
