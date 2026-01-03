# Milvus Setup and Troubleshooting Guide

This guide helps you set up Milvus properly and troubleshoot common issues.

## Table of Contents

1. [Recommended Setup (Docker Compose)](#recommended-setup-docker-compose)
2. [Alternative Setup (Standalone Docker)](#alternative-setup-standalone-docker)
3. [Troubleshooting](#troubleshooting)
4. [Verification](#verification)

## Recommended Setup (Docker Compose)

The recommended way to run Milvus is using Docker Compose, which includes all required dependencies.

### Prerequisites

- Docker Desktop installed and running
- At least 8GB RAM available
- 10GB free disk space

### Step 1: Stop Any Existing Containers

```bash
# Stop and remove any existing Milvus containers
docker stop milvus-standalone milvus-etcd milvus-minio 2>/dev/null
docker rm milvus-standalone milvus-etcd milvus-minio 2>/dev/null

# Clean up volumes (optional - only if you want to start fresh)
docker volume prune -f
```

### Step 2: Start Milvus with Docker Compose

```bash
# From the project root directory
docker-compose up -d
```

### Step 3: Check Container Status

```bash
# Check if all containers are running
docker-compose ps

# You should see 3 containers running:
# - milvus-standalone
# - milvus-etcd
# - milvus-minio
```

### Step 4: View Logs

```bash
# View all logs
docker-compose logs

# View Milvus logs specifically
docker-compose logs standalone

# Follow logs in real-time
docker-compose logs -f standalone
```

### Step 5: Stop Milvus

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Alternative Setup (Standalone Docker)

If you prefer a simpler setup without dependencies, you can use Milvus Lite (not recommended for production).

### Using Milvus Standalone (May Exit)

The simple standalone command often fails because it needs etcd and minio:

```bash
# This often exits immediately (NOT RECOMMENDED)
docker run -d --name milvus_standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:latest
```

### Better Standalone Setup

Use this improved standalone setup:

```bash
# Create network
docker network create milvus

# Start etcd
docker run -d \
  --name milvus-etcd \
  --network milvus \
  -e ETCD_AUTO_COMPACTION_MODE=revision \
  -e ETCD_AUTO_COMPACTION_RETENTION=1000 \
  -e ETCD_QUOTA_BACKEND_BYTES=4294967296 \
  quay.io/coreos/etcd:v3.5.5 \
  etcd -advertise-client-urls=http://127.0.0.1:2379 \
  -listen-client-urls http://0.0.0.0:2379 \
  --data-dir /etcd

# Start MinIO
docker run -d \
  --name milvus-minio \
  --network milvus \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ACCESS_KEY=minioadmin \
  -e MINIO_SECRET_KEY=minioadmin \
  minio/minio:RELEASE.2023-03-20T20-16-18Z \
  minio server /minio_data --console-address ":9001"

# Start Milvus
docker run -d \
  --name milvus-standalone \
  --network milvus \
  -p 19530:19530 -p 9091:9091 \
  -e ETCD_ENDPOINTS=milvus-etcd:2379 \
  -e MINIO_ADDRESS=milvus-minio:9000 \
  milvusdb/milvus:v2.3.3 \
  milvus run standalone
```

## Troubleshooting

### Issue 1: Container Exits Immediately

**Symptoms:**
```bash
docker ps -a
# Shows milvus-standalone with status "Exited"
```

**Causes:**
- Missing etcd dependency
- Missing MinIO dependency
- Insufficient resources
- Port conflicts

**Solutions:**

1. **Use Docker Compose (Recommended):**
   ```bash
   docker-compose up -d
   ```

2. **Check logs for errors:**
   ```bash
   docker logs milvus-standalone
   ```

3. **Ensure sufficient resources:**
   - Docker Desktop: Settings → Resources
   - Allocate at least 4GB RAM
   - Allocate at least 2 CPUs

4. **Check for port conflicts:**
   ```bash
   # Check if ports are in use
   lsof -i :19530  # macOS/Linux
   netstat -ano | findstr :19530  # Windows
   ```

### Issue 2: Connection Refused

**Symptoms:**
```
Error: failed to connect to milvus: connection refused
```

**Solutions:**

1. **Check if Milvus is running:**
   ```bash
   docker ps | grep milvus
   ```

2. **Check Milvus health:**
   ```bash
   curl http://localhost:9091/healthz
   # Should return: OK
   ```

3. **Wait for startup:**
   Milvus takes 30-60 seconds to fully start. Check logs:
   ```bash
   docker-compose logs -f standalone
   # Wait for: "Milvus Proxy successfully started"
   ```

4. **Restart services:**
   ```bash
   docker-compose restart
   ```

### Issue 3: Out of Memory

**Symptoms:**
```
Container exits with code 137
```

**Solutions:**

1. **Increase Docker memory:**
   - Docker Desktop → Settings → Resources
   - Increase Memory to at least 8GB

2. **Close other applications**

3. **Use Milvus Lite for development:**
   ```bash
   pip install milvus
   # Uses embedded Milvus (no Docker needed)
   ```

### Issue 4: Permission Denied

**Symptoms:**
```
Error: permission denied while trying to connect to Docker daemon
```

**Solutions:**

1. **Start Docker Desktop**

2. **Add user to docker group (Linux):**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Run with sudo (not recommended):**
   ```bash
   sudo docker-compose up -d
   ```

### Issue 5: Network Issues

**Symptoms:**
```
Error: cannot connect to etcd
Error: cannot connect to minio
```

**Solutions:**

1. **Recreate network:**
   ```bash
   docker-compose down
   docker network prune -f
   docker-compose up -d
   ```

2. **Check network:**
   ```bash
   docker network ls
   docker network inspect milvus
   ```

## Verification

### 1. Check Container Status

```bash
# All containers should be "Up"
docker-compose ps

# Expected output:
# NAME                STATUS
# milvus-standalone   Up (healthy)
# milvus-etcd        Up (healthy)
# milvus-minio       Up (healthy)
```

### 2. Check Milvus Health

```bash
# Should return "OK"
curl http://localhost:9091/healthz
```

### 3. Test Connection with Python

```python
from pymilvus import connections, utility

# Connect to Milvus
connections.connect(
    alias="default",
    host='localhost',
    port='19530'
)

# Check connection
print("Connected to Milvus!")
print(f"Server version: {utility.get_server_version()}")

# Disconnect
connections.disconnect("default")
```

### 4. Test with RAG Application

```bash
# Test connection
python -c "from src.rag_app.core.milvus_manager import MilvusManager; m = MilvusManager(); m.connect(); print('Success!')"
```

## Best Practices

1. **Always use Docker Compose** for development and production
2. **Monitor logs** during startup: `docker-compose logs -f`
3. **Wait for health checks** before connecting (30-60 seconds)
4. **Allocate sufficient resources** (8GB RAM, 2 CPUs minimum)
5. **Use volumes** for data persistence
6. **Regular backups** of the volumes directory

## Quick Commands Reference

```bash
# Start Milvus
docker-compose up -d

# Stop Milvus
docker-compose down

# View logs
docker-compose logs -f standalone

# Restart Milvus
docker-compose restart

# Check status
docker-compose ps

# Clean everything (including data)
docker-compose down -v

# Check health
curl http://localhost:9091/healthz

# Access MinIO console
open http://localhost:9001
# Login: minioadmin / minioadmin
```

## System Requirements

### Minimum:
- 4GB RAM
- 2 CPU cores
- 5GB disk space

### Recommended:
- 8GB RAM
- 4 CPU cores
- 20GB disk space

## Additional Resources

- [Milvus Documentation](https://milvus.io/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Milvus GitHub Issues](https://github.com/milvus-io/milvus/issues)

## Getting Help

If you're still experiencing issues:

1. Check the logs: `docker-compose logs standalone`
2. Verify system resources: `docker stats`
3. Check Docker version: `docker --version` (should be 20.10+)
4. Review Milvus documentation
5. Open an issue on GitHub with logs and error messages