@echo off
REM Script d'installation automatique pour Windows
REM Projet: Supervision Routeur Cisco

echo 🚀 Installation automatique du projet de supervision Routeur Cisco
echo ==================================================================

REM Vérification de Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Docker Desktop et redémarrer
    pause
    exit /b 1
)

REM Vérification de Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose n'est pas installé
    echo Veuillez installer Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker et Docker Compose sont installés

REM Nettoyage des anciens conteneurs
echo 🧹 Nettoyage des anciens conteneurs...
docker-compose down -v 2>nul
docker system prune -f

REM Création des répertoires nécessaires
echo 📁 Création des répertoires nécessaires...
if not exist "static" mkdir static
if not exist "media" mkdir media
if not exist "tmp\metrics" mkdir tmp\metrics

REM Configuration des variables d'environnement
echo ⚙️  Configuration des variables d'environnement...
if not exist ".env" (
    echo # Configuration de la base de données > .env
    echo DATABASE=postgres >> .env
    echo SQL_HOST=postgres >> .env
    echo SQL_PORT=5432 >> .env
    echo POSTGRES_DB=router_supervision >> .env
    echo POSTGRES_USER=postgres >> .env
    echo POSTGRES_PASSWORD=postgres123 >> .env
    echo. >> .env
    echo # Configuration Django >> .env
    echo DJANGO_SETTINGS_MODULE=router_supervisor.src.settings >> .env
    echo SECRET_KEY=your-secret-key-here-change-in-production >> .env
    echo DEBUG=True >> .env
    echo. >> .env
    echo # Configuration InfluxDB >> .env
    echo INFLUXDB_V2_URL=http://influxdb:8086 >> .env
    echo INFLUXDB_V2_ORG=router_supervision >> .env
    echo INFLUXDB_V2_BUCKET=router_metrics >> .env
    echo INFLUXDB_V2_TOKEN=your-influxdb-token >> .env
    echo. >> .env
    echo # Configuration réseau >> .env
    echo ROUTER_IP=192.168.1.1 >> .env
    echo SNMP_COMMUNITY=public >> .env
    echo SNMP_PORT=161 >> .env
    echo ✅ Fichier .env créé
) else (
    echo ℹ️  Fichier .env existant conservé
)

REM Construction et démarrage
echo 🔨 Construction et démarrage des services...
echo 📦 Construction des images Docker...
docker-compose build --no-cache

echo 🚀 Démarrage des services...
docker-compose up -d

echo ⏳ Attente que les services soient prêts...
timeout /t 30 /nobreak >nul

echo 📊 Vérification du statut des services...
docker-compose ps

echo.
echo 🎉 Installation terminée avec succès!
echo =====================================
echo.
echo 🌐 Accès aux services:
echo   Dashboard:    http://localhost:8080/
echo   Settings:     http://localhost:8080/settings/
echo   Alertes:      http://localhost:8080/alertes/
echo   Thresholds:   http://localhost:8080/thresholds/
echo   InfluxDB:     http://localhost:8086/
echo   pgAdmin:      http://localhost:5050/
echo.
echo 👤 Compte administrateur:
echo   Utilisateur:  admin
echo   Mot de passe: admin123
echo.
echo 🔧 Commandes utiles:
echo   Arrêter:      docker-compose down
echo   Redémarrer:   docker-compose restart
echo   Logs:         docker-compose logs -f
echo   Reconstruire: docker-compose up --build
echo.
echo ✅ Installation réussie! Votre projet est maintenant prêt à utiliser.
echo.
echo Appuyez sur une touche pour ouvrir le dashboard...
pause >nul
start http://localhost:8080/
