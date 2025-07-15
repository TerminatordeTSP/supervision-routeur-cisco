# 🚨 PROBLÈME DE PORT RÉSOLU !

Si vous avez l'erreur `failed to bind host port for 0.0.0.0:8080` lors du `docker compose up -d`, c'est que le port 8080 est déjà utilisé sur votre machine.

## ✅ Solution rapide :

1. **Ouvrez le fichier `.env`** à la racine du projet
2. **Changez la ligne** :
   ```
   CADDY_PORT=8080
   ```
   **en** :
   ```
   CADDY_PORT=8081
   ```
   (ou un autre port libre : 8082, 9000, etc.)

3. **Redémarrez** :
   ```bash
   docker compose down
   docker compose up -d
   ```

4. **Accédez à l'application** sur : `http://localhost:8081` (ou le port que vous avez choisi)

## 🔍 Ports utilisés par défaut :
- **Application principale** : `localhost:8081` (ou votre port choisi)
- **Django direct** : `localhost:8080` 
- **pgAdmin** : `localhost:5050`
- **InfluxDB** : `localhost:8086`

## 📋 Services disponibles :
- **Supervision des routeurs** : http://localhost:8081
- **Administration BD** : http://localhost:5050 (admin@telecom-sudparis.eu / admin)
- **InfluxDB** : http://localhost:8086 (admin / admin123456)

---
*Problème résolu ? L'application devrait maintenant démarrer sans erreur ! 🎉*
