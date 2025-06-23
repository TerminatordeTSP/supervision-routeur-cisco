FROM almalinux:9

# Mise à jour et installation des dépendances système
RUN dnf install -y --allowerasing \
    python3 python3-pip python3-devel gcc \
    nc curl git libpq-devel && \
    dnf clean all

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
RUN pip3 install psycopg2-binary gunicorn

# Installation de Telegraf ARM/x86 compatible via dépôt officiel
RUN curl -s https://repos.influxdata.com/influxdata-archive.key | gpg --dearmor > /etc/pki/rpm-gpg/influxdata.gpg && \
    echo -e "[influxdata]\nname=InfluxData Repository - RHEL\nbaseurl=https://repos.influxdata.com/rhel/9/\$basearch/stable\nenabled=1\ngpgcheck=1\ngpgkey=file:///etc/pki/rpm-gpg/influxdata.gpg" > /etc/yum.repos.d/influxdata.repo && \
    dnf install -y telegraf && \
    dnf clean all

# Créer les répertoires nécessaires (si besoin)
RUN mkdir -p /code/static /code/media

# Copier le code source Django
COPY router_supervisor/ /code/router_supervisor/

# Scripts de lancement
COPY entrypoint.sh /entrypoint.sh
COPY start /start
RUN chmod +x /entrypoint.sh /start

# Exposer le port Django
EXPOSE 8080/tcp

# Healthcheck Django
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health/ || exit 1

# Entrée du conteneur
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start"]