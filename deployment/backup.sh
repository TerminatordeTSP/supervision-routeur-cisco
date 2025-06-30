#!/bin/bash

# Script de sauvegarde pour supervision-routeur-cisco
# Sauvegarde les données PostgreSQL et InfluxDB

set -e

# Variables
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="postgres_prod"
INFLUXDB_CONTAINER="influxdb_prod"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[DEBUG] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Créer le répertoire de sauvegarde
mkdir -p "$BACKUP_DIR"

log_info "Début de la sauvegarde - $DATE"

# Sauvegarde PostgreSQL
log_info "Sauvegarde de PostgreSQL..."
if docker exec "$POSTGRES_CONTAINER" pg_dump -U user routerdb > "$BACKUP_DIR/postgres_backup_$DATE.sql"; then
    log_success "Sauvegarde PostgreSQL créée: postgres_backup_$DATE.sql"
else
    log_error "Échec de la sauvegarde PostgreSQL"
    exit 1
fi

# Sauvegarde InfluxDB
log_info "Sauvegarde d'InfluxDB..."
if docker exec "$INFLUXDB_CONTAINER" influx backup "/backup/influxdb_backup_$DATE" --org telecom-sudparis --token my-super-secret-auth-token; then
    log_success "Sauvegarde InfluxDB créée: influxdb_backup_$DATE"
else
    log_error "Échec de la sauvegarde InfluxDB"
    exit 1
fi

# Compresser les sauvegardes
log_info "Compression des sauvegardes..."
tar -czf "$BACKUP_DIR/supervision_backup_$DATE.tar.gz" \
    -C "$BACKUP_DIR" \
    "postgres_backup_$DATE.sql" \
    "influxdb_backup_$DATE"

# Nettoyer les fichiers temporaires
rm -f "$BACKUP_DIR/postgres_backup_$DATE.sql"
rm -rf "$BACKUP_DIR/influxdb_backup_$DATE"

log_success "Sauvegarde complète: supervision_backup_$DATE.tar.gz"

# Nettoyer les anciennes sauvegardes (garder les 7 dernières)
log_info "Nettoyage des anciennes sauvegardes..."
cd "$BACKUP_DIR"
ls -t supervision_backup_*.tar.gz | tail -n +8 | xargs -r rm -f

log_success "Sauvegarde terminée avec succès"
