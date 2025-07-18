FROM almalinux:9

RUN dnf install -y --allowerasing \
    python3 python3-pip python3-devel gcc \
    nc curl git libpq-devel \
    net-snmp net-snmp-utils net-snmp-libs \
    && dnf clean all

# Téléchargement des MIBs SNMP manquants
RUN mkdir -p /usr/share/snmp/mibs \
    && curl -o /usr/share/snmp/mibs/IF-MIB https://mibs.observium.org/mibs/IF-MIB \
    && curl -o /usr/share/snmp/mibs/SNMPv2-MIB https://mibs.observium.org/mibs/SNMPv2-MIB \
    && curl -o /usr/share/snmp/mibs/SNMPv2-SMI https://mibs.observium.org/mibs/SNMPv2-SMI \
    && curl -o /usr/share/snmp/mibs/SNMPv2-TC https://mibs.observium.org/mibs/SNMPv2-TC

# Variables d'environnement
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="router_supervisor.prod_settings"
ENV PYTHONPATH=/code

# Répertoire de travail
WORKDIR /code

# Installation des dépendances Python
COPY requirements.txt /code/
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --use-pep517 -r requirements.txt
RUN pip3 install psycopg2-binary gunicorn influxdb-client

# Créer les répertoires nécessaires (si besoin)
RUN mkdir -p /code/static /code/media


# Copier le code source Django, le client InfluxDB et les scripts
COPY router_supervisor/ /code/router_supervisor/
COPY gunicorn.conf.py /code/
COPY scripts/ /code/scripts/
COPY pipeline.py /code/

# Scripts de lancement
COPY entrypoint.sh /entrypoint.sh
COPY start /start
RUN chmod +x /entrypoint.sh /start /code/scripts/clean_migrations.sh

# Exposer le port Django
EXPOSE 8080/tcp

# Healthcheck Django
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health/ || exit 1

# Entrée du conteneur
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start"]