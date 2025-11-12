# Vector Search Service Deployment Guide

This guide covers deploying the vector search service to your unRAID self-hosted runner using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Self-Hosted Runner Setup](#self-hosted-runner-setup)
3. [GitHub Secrets Configuration](#github-secrets-configuration)
4. [Initial Deployment](#initial-deployment)
5. [Monitoring and Management](#monitoring-and-management)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### On Your unRAID Server

**Required Software:**
- Docker (should be pre-installed on unRAID)
- Docker Compose
- Python 3.11+ (for indexing script)
- Git

**Install Docker Compose (if not already installed):**
```bash
# Check if docker-compose is installed
docker-compose --version

# If not installed, install via unRAID Community Applications
# Or manually:
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

**Install Python Dependencies (for indexing):**
```bash
cd /path/to/doc-repo/vector_search
pip install -r requirements.txt
```

---

## Self-Hosted Runner Setup

### 1. Create GitHub Self-Hosted Runner

**On GitHub:**
1. Go to your repository: `https://github.com/JamesPrial/doc-repo`
2. Navigate to **Settings** → **Actions** → **Runners**
3. Click **New self-hosted runner**
4. Select **Linux** as the operating system
5. Follow the installation commands provided

**On Your unRAID Server:**
```bash
# Create a directory for the runner
mkdir -p /mnt/user/appdata/github-runner
cd /mnt/user/appdata/github-runner

# Download and extract the runner (use commands from GitHub)
curl -o actions-runner-linux-x64-2.XXX.X.tar.gz -L https://github.com/actions/runner/releases/download/vX.XXX.X/actions-runner-linux-x64-2.XXX.X.tar.gz
tar xzf ./actions-runner-linux-x64-2.XXX.X.tar.gz

# Configure the runner (use token from GitHub)
./config.sh --url https://github.com/JamesPrial/doc-repo --token YOUR_TOKEN_HERE

# Install as a service
sudo ./svc.sh install
sudo ./svc.sh start
```

### 2. Verify Runner Status

- Go back to **Settings** → **Actions** → **Runners** on GitHub
- Your runner should appear with a green dot (online)

---

## GitHub Secrets Configuration

### 1. Get Google API Key

1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the generated key

### 2. Add Secret to GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GOOGLE_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

---

## Initial Deployment

### Option 1: Automatic Deployment (Recommended)

The workflow will automatically deploy when:
- Documentation changes are pushed to the `main` branch
- Changes occur in `claude/docs/**` or `reddit/*.md`
- Changes occur in `vector_search/**`

**To trigger manually:**
1. Go to **Actions** tab on GitHub
2. Select **Deploy Vector Database**
3. Click **Run workflow**
4. Optionally enable **Force full re-indexing**
5. Click **Run workflow**

### Option 2: Manual Local Deployment

If you want to deploy manually on your unRAID server:

```bash
# Navigate to the repository
cd /path/to/doc-repo/vector_search

# Create .env file with API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Initial indexing (first time only)
python index_documents.py

# Build and start the Docker container
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## Monitoring and Management

### Check Service Health

```bash
# Quick health check
curl http://localhost:8000/health

# Detailed statistics
curl http://localhost:8000/stats

# Pretty-printed JSON
curl http://localhost:8000/health | python -m json.tool
```

### View Container Logs

```bash
cd /path/to/doc-repo/vector_search

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View specific service logs
docker-compose logs vector-search-api
```

### Restart the Service

```bash
cd /path/to/doc-repo/vector_search

# Restart container
docker-compose restart

# Stop container
docker-compose down

# Start container
docker-compose up -d
```

### Manual Re-indexing

If you need to manually re-index documents:

```bash
cd /path/to/doc-repo/vector_search

# Incremental indexing (only changed docs)
python index_documents.py

# Full re-indexing (reset database)
python index_documents.py --reset

# Test search after indexing
python index_documents.py --test-search "your query"
```

### Update the Service

```bash
cd /path/to/doc-repo

# Pull latest changes
git pull origin main

# Navigate to vector_search
cd vector_search

# Rebuild and restart container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
- Missing `GOOGLE_API_KEY` in environment
- ChromaDB directory permissions
- Port 8000 already in use

**Solutions:**
```bash
# Check if port 8000 is in use
netstat -tuln | grep 8000

# Fix permissions
chmod -R 755 chroma_db

# Verify .env file exists
cat .env
```

### Health Check Failing

**Verify the service is running:**
```bash
docker-compose ps
```

**Check container health:**
```bash
docker inspect vector-search-api | grep -A 10 Health
```

**Test health endpoint manually:**
```bash
# From inside the container
docker-compose exec vector-search-api curl http://localhost:8000/health

# From host
curl http://localhost:8000/health
```

### Indexing Errors

**Common issues:**
- Google API key invalid or rate limited
- Documentation files not accessible
- Out of memory

**Solutions:**
```bash
# Verify API key works
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=YOUR_API_KEY"

# Check available memory
free -h

# Monitor indexing progress
python index_documents.py 2>&1 | tee indexing.log
```

### GitHub Actions Workflow Failing

**Check workflow logs:**
1. Go to **Actions** tab on GitHub
2. Select the failed workflow run
3. Click on the job to see detailed logs

**Common issues:**
- Self-hosted runner offline
- Missing GitHub secret (GOOGLE_API_KEY)
- Docker not available on runner
- Network connectivity issues

**Verify runner status:**
```bash
# On unRAID server
cd /mnt/user/appdata/github-runner
./svc.sh status

# Restart runner if needed
sudo ./svc.sh restart
```

### Container Using Too Much Memory

**Check resource usage:**
```bash
docker stats vector-search-api
```

**Limit resources in docker-compose.yml:**
```yaml
services:
  vector-search-api:
    # ... existing config ...
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
```

---

## Network Access

### Accessing from Other Devices

By default, the service is accessible at `http://localhost:8000`. To access from other devices on your network:

1. **Find your unRAID server IP:**
   ```bash
   ip addr show | grep inet
   ```

2. **Access the service:**
   - Health check: `http://YOUR_UNRAID_IP:8000/health`
   - API docs: `http://YOUR_UNRAID_IP:8000/docs`
   - Search endpoint: `http://YOUR_UNRAID_IP:8000/search`

3. **Configure firewall (if needed):**
   - Ensure port 8000 is open on your unRAID server
   - Add firewall rule if using iptables

### Reverse Proxy Setup (Optional)

If you want to use a reverse proxy (nginx, Caddy, Traefik):

**Example nginx config:**
```nginx
server {
    listen 80;
    server_name vector-search.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Workflow Behavior

### Automatic Triggers

The workflow automatically deploys when:
- Documentation changes in `claude/docs/**` or `reddit/*.md`
- Code changes in `vector_search/**`
- Pushed to `main` branch

### Smart Re-indexing

The workflow intelligently handles indexing:
- **Docs changed:** Re-indexes documents
- **Code changed only:** Redeploys container without re-indexing
- **Manual trigger with force:** Full database reset and re-index

### Concurrency Control

- Only one deployment runs at a time
- New deployments wait for current deployment to finish
- No concurrent deployments to prevent conflicts

---

## Best Practices

1. **Monitor API usage:** Check Google API quotas (1,500 requests/day on free tier)
2. **Regular backups:** Backup `chroma_db/` directory periodically
3. **Log rotation:** Configure Docker log rotation to prevent disk space issues
4. **Health monitoring:** Set up automated health checks (e.g., cron job + curl)
5. **Security:** Keep API key secure, never commit to repository

---

## Support and Resources

- **Vector Search Documentation:** See main README.md
- **GitHub Actions Logs:** Check Actions tab for deployment history
- **API Documentation:** http://localhost:8000/docs (when service is running)
- **ChromaDB Docs:** https://docs.trychroma.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

## Quick Reference

```bash
# Deploy manually
cd vector_search && docker-compose up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Stop service
docker-compose down

# Re-index docs
python index_documents.py

# Full reset and re-index
python index_documents.py --reset
```
