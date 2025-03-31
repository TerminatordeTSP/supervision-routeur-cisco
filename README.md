# Projet de Surveillance Routeur Cisco

## Styles et conventions CSS

Ce projet utilise :
- Boosted 5.3.3 (version Orange de Bootstrap)
- Bootstrap Icons 1.11.1
- Styles personnalisés dans `staticfiles/css/dashboard.css`

### Comment ajouter une nouvelle page

1. Créez votre template en héritant de base.html :
```html
{% extends "base.html" %}
{% block content %}
   <!-- Votre contenu ici -->
{% endblock %}