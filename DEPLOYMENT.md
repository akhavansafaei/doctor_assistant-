# 🚀 Deployment Guide

Complete guide for deploying the AI Doctor Chatbot in various environments.

---

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Prerequisites
```bash
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Qdrant (latest)
- API Keys (OpenAI, Anthropic, Cohere)
```

### Setup Steps

1. **Clone and Setup Environment**
```bash
git clone <repository>
cd doctor_assistant-/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp ../.env.example ../.env
# Edit .env with your settings
```

3. **Start Databases**
```bash
# PostgreSQL
sudo systemctl start postgresql
createdb doctor_assistant

# Redis
sudo systemctl start redis

# Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

4. **Run Application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker Deployment

### Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build backend
```

### Production Docker Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: doctor-ai-backend:latest
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: always
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Production Deployment

### System Requirements

**Minimum:**
- 4 CPU cores
- 8 GB RAM
- 50 GB SSD storage
- Ubuntu 22.04 LTS or similar

**Recommended:**
- 8 CPU cores
- 16 GB RAM
- 100 GB SSD storage
- Load balancer

### Installation Steps

1. **Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3-pip postgresql-15 redis nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Setup Application**
```bash
# Clone repository
cd /opt
sudo git clone <repository> doctor-ai
cd doctor-ai

# Configure environment
sudo cp .env.example .env
sudo nano .env  # Add production settings

# Set permissions
sudo chown -R www-data:www-data /opt/doctor-ai
```

3. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/doctor-ai
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/doctor-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

5. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/doctor-ai.service
```

```ini
[Unit]
Description=AI Doctor Chatbot
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/doctor-ai/backend
Environment="PATH=/opt/doctor-ai/backend/venv/bin"
ExecStart=/opt/doctor-ai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable doctor-ai
sudo systemctl start doctor-ai
sudo systemctl status doctor-ai
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.large or larger
   - Storage: 100 GB SSD
   - Security Group: Allow ports 22, 80, 443, 8000

2. **Configure EC2**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
# Follow production deployment steps above
```

#### Using ECS (Docker)

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name doctor-ai-backend
```

2. **Build and Push Docker Image**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker build -t doctor-ai-backend .
docker tag doctor-ai-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/doctor-ai-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/doctor-ai-backend:latest
```

3. **Create ECS Task Definition** (use AWS Console or CLI)

4. **Deploy to ECS**

#### Using RDS for Database
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier doctor-ai-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword \
  --allocated-storage 100
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and Push to GCR**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/doctor-ai-backend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy doctor-ai-backend \
  --image gcr.io/YOUR_PROJECT/doctor-ai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://...,OPENAI_API_KEY=sk-..."
```

### Azure Deployment

#### Using Azure Container Instances

```bash
az container create \
  --resource-group doctor-ai-rg \
  --name doctor-ai-backend \
  --image YOUR_REGISTRY/doctor-ai-backend:latest \
  --cpu 2 --memory 4 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL="..." \
    OPENAI_API_KEY="..."
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl http://your-domain.com/health

# Database connectivity
curl http://your-domain.com/api/v1/health/db

# Vector database
curl http://your-domain.com/api/v1/health/qdrant
```

### Logging

**View Application Logs:**
```bash
# Docker
docker-compose logs -f backend

# Systemd
sudo journalctl -u doctor-ai -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

### Monitoring Setup

**Prometheus + Grafana:**

1. Add to `docker-compose.yml`:
```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

2. Create `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'doctor-ai-backend'
    static_configs:
      - targets: ['backend:8000']
```

### Backup Strategy

**Database Backups:**
```bash
# PostgreSQL
pg_dump -U doctor_ai doctor_assistant > backup_$(date +%Y%m%d).sql

# Automated daily backups
echo "0 2 * * * pg_dump -U doctor_ai doctor_assistant > /backups/db_$(date +\%Y\%m\%d).sql" | crontab -
```

**Vector Database Backups:**
```bash
# Qdrant snapshots
curl -X POST 'http://localhost:6333/collections/medical_knowledge/snapshots'
```

### Security Hardening

1. **Firewall Configuration**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **Fail2Ban for SSH**
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

3. **Regular Updates**
```bash
# Automated security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### Performance Tuning

**PostgreSQL:**
```sql
-- Adjust based on available RAM
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '50MB';
```

**Redis:**
```bash
# In redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

**Uvicorn Workers:**
```bash
# Number of workers = (2 x CPU cores) + 1
uvicorn app.main:app --workers 9 --host 0.0.0.0 --port 8000
```

---

## Troubleshooting

### Common Issues

**Issue: Database Connection Failed**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Issue: Out of Memory**
```bash
# Check memory usage
free -h

# Check Docker container limits
docker stats

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Issue: Slow Response Times**
```bash
# Check LLM API latency
curl -w "@curl-format.txt" -o /dev/null -s http://api.openai.com/v1/models

# Check database query performance
# Enable query logging in PostgreSQL

# Add Redis caching for frequent queries
```

---

## Scaling

### Horizontal Scaling

**Load Balancer Setup (Nginx):**
```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location / {
        proxy_pass http://backend_servers;
    }
}
```

### Database Scaling

**Read Replicas:**
```python
# In production config
DATABASES = {
    'default': {
        'ENGINE': 'postgresql',
        'HOST': 'primary-db',
    },
    'replica': {
        'ENGINE': 'postgresql',
        'HOST': 'replica-db',
    }
}
```

---

**For more help, see the main [README.md](./README.md) or open an issue.**
