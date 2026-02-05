# Deployment Guide

## System Requirements

- Python 3.8+
- 2GB RAM minimum
- 10GB storage minimum
- Internet connection for API access

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd news-satire-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize database:**
   ```bash
   python -c "from src.storage.archive import ArchiveManager; ArchiveManager()"
   ```

## Configuration

### Environment Variables

- `NEWSDATA_API_KEY`: Your NewsData.io API key (provided)
- `DATABASE_URL`: Database connection string (default: sqlite:///articles.db)
- `OPENAI_API_KEY`: Optional OpenAI API key for advanced generation
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### Publishing Schedule

The system is configured to publish at:
- 8:00 AM CST
- 8:00 PM CST

Modify `Config.PUBLISH_TIMES` in `src/utils/config.py` to change schedule.

## Running the System

### Production Mode

```bash
python main.py
```

This starts the scheduler which will run publishing cycles at the configured times.

### Test Mode

```bash
python main.py --test
```

This runs an immediate publishing cycle for testing purposes.

## Deployment Options

### Option 1: Local Development

Run directly on your local machine for development and testing.

### Option 2: Server Deployment

Deploy to a Linux server with systemd:

1. **Create systemd service:**
   ```ini
   [Unit]
   Description=News Satire System
   After=network.target

   [Service]
   Type=simple
   User=satire
   WorkingDirectory=/opt/news-satire-system
   ExecStart=/usr/bin/python3 /opt/news-satire-system/main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start:**
   ```bash
   sudo systemctl enable satire-system
   sudo systemctl start satire-system
   ```

### Option 3: Docker Deployment

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   CMD ["python", "main.py"]
   ```

2. **Build and run:**
   ```bash
   docker build -t satire-system .
   docker run -d --name satire-system satire-system
   ```

### Option 4: Cloud Deployment

Deploy to AWS Lambda, Google Cloud Functions, or similar serverless platforms for automated execution.

## Monitoring

### Logs

Logs are stored in the `logs/` directory with daily rotation:
- `logs/satire_system_YYYYMMDD.log`

### Health Checks

Monitor the following:
- API response times
- Article generation success rate
- Database connectivity
- Disk space usage

### Alerts

Set up alerts for:
- Failed publishing cycles
- API rate limits
- Database errors
- Low disk space

## Backup Strategy

### Database Backup

For SQLite:
```bash
cp articles.db backup/articles_$(date +%Y%m%d_%H%M%S).db
```

### Article Archive Backup

The `data/articles/` directory contains JSON backups of all articles.

## Security Considerations

1. **API Keys:** Store in environment variables, not in code
2. **Database:** Use proper authentication in production
3. **Network:** Restrict API access to required endpoints only
4. **File Permissions:** Restrict access to sensitive files

## Performance Optimization

1. **Database:** Consider PostgreSQL for high-volume deployments
2. **Caching:** Implement Redis for API response caching
3. **CDN:** Use CDN for XKCD comic images
4. **Load Balancing:** Multiple instances for high availability

## Troubleshooting

### Common Issues

1. **API Rate Limits:**
   - Check API key quotas
   - Implement backoff retry logic

2. **Database Locks:**
   - Use connection pooling
   - Implement proper transaction handling

3. **Memory Usage:**
   - Monitor article archive size
   - Implement cleanup for old articles

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## Scaling

### Horizontal Scaling

- Deploy multiple instances behind a load balancer
- Use shared database (PostgreSQL)
- Implement distributed locking for publishing cycles

### Vertical Scaling

- Increase RAM for larger article archives
- Use SSD storage for faster database operations
- Optimize database queries and indexes

## Maintenance

### Regular Tasks

1. **Log Cleanup:** Remove logs older than 30 days
2. **Database Maintenance:** Run vacuum and analyze operations
3. **Archive Cleanup:** Remove very old articles if needed
4. **API Key Rotation:** Update API keys periodically

### Updates

1. **Dependencies:** Regularly update Python packages
2. **System:** Apply security patches
3. **Code:** Deploy updates during off-peak hours
