FROM almalinux:9

# Installer les dépendances
RUN dnf install -y --allowerasing python3 python3-pip python3-devel nc curl

ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="prod_settings"

WORKDIR /code

COPY requirements.txt /code/
RUN pip3 install --upgrade 'setuptools' 'wheel' 'pip'
RUN pip3 install --use-pep517 -r requirements.txt
RUN pip3 install psycopg2-binary gunicorn

# Installer Telegraf avec la version spécifique
RUN dnf install -y git && \
    dnf install -y https://dl.influxdata.com/telegraf/releases/telegraf-1.30.0-1.x86_64.rpm

# Copier le code de l'application
COPY router_supervisor/ /code/

# Créer les répertoires pour les fichiers statiques et média
RUN mkdir -p /code/static /code/media

# Copier les scripts
COPY entrypoint.sh /entrypoint.sh
COPY start /start
RUN chmod +x /start /entrypoint.sh

# Exposer le port et définir le healthcheck
EXPOSE 8080/tcp
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "120"]