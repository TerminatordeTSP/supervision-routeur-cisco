FROM telegraf:1.30.0

# Installation des dépendances
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    netcat-openbsd \
    curl \
    vim \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /etc/telegraf

# Scripts personnalisés
COPY init.sh /etc/telegraf/init.sh
COPY generate_test_data.py /etc/telegraf/generate_test_data.py
COPY send_test_data.py /etc/telegraf/send_test_data.py

# Créer les répertoires nécessaires
RUN mkdir -p /tmp/metrics /var/log/telegraf \
    && chmod +x /etc/telegraf/init.sh \
    && chmod +x /etc/telegraf/generate_test_data.py \
    && chmod +x /etc/telegraf/send_test_data.py

# Utiliser le script d'initialisation comme point d'entrée
ENTRYPOINT ["/etc/telegraf/init.sh"]