#!/bin/bash

echo "=== DJANGO CONTAINER TROUBLESHOOTING ==="
echo "Date: $(date)"
echo "Server: $(hostname)"
echo ""

echo "=== 1. CHECK DOCKER SERVICE ==="
sudo systemctl status docker | head -10
echo ""

echo "=== 2. CHECK DOCKER COMPOSE VERSION ==="
docker-compose --version
echo ""

echo "=== 3. CHECK CURRENT DIRECTORY ==="
pwd
ls -la | head -10
echo ""

echo "=== 4. CHECK DOCKER CONTAINERS STATUS ==="
docker ps -a
echo ""

echo "=== 5. CHECK DOCKER COMPOSE SERVICES ==="
if [ -f docker-compose.yml ]; then
    echo "Using docker-compose.yml:"
    docker-compose ps
elif [ -f deployment/docker-compose.prod.yml ]; then
    echo "Using deployment/docker-compose.prod.yml:"
    docker-compose -f deployment/docker-compose.prod.yml ps
else
    echo "No docker-compose file found!"
fi
echo ""

echo "=== 6. CHECK DJANGO CONTAINER LOGS (last 20 lines) ==="
# Try different container names
for container in router_django router_django_prod supervision-routeur-cisco-router_django; do
    if docker ps -a --format "table {{.Names}}" | grep -q "$container"; then
        echo "Found container: $container"
        docker logs --tail 20 "$container"
        break
    fi
done
echo ""

echo "=== 7. CHECK PORTS IN USE ==="
sudo netstat -tlnp | grep -E ":(80|8080|443)" || echo "No web ports found"
echo ""

echo "=== 8. CHECK DISK SPACE ==="
df -h / | head -2
echo ""

echo "=== 9. CHECK MEMORY USAGE ==="
free -h
echo ""

echo "=== 10. CHECK DOCKER IMAGES ==="
docker images | grep -E "(django|supervision|router)" || echo "No Django/router images found"
echo ""

echo "=== TROUBLESHOOTING COMPLETE ==="
echo "Please share this output for diagnosis."
