# Saturn - AI Cloud Infrastructure Manager

A powerful Discord bot for managing AWS cloud infrastructure and Docker containers with integrated monitoring and alerting capabilities. Saturn provides a seamless interface for managing cloud resources, containers, and infrastructure monitoring through Discord commands.

## Features

### AWS Infrastructure Management
- **EC2 Instance Control**
  - `/instance start` - Start EC2 instance
  - `/instance stop` - Stop EC2 instance
  - `/instance status` - Get detailed instance status
  - `/aws_test` - Test AWS connectivity

### Docker Container Management
- **Container Operations**
  - `/containers` - List all Docker containers with status
  - `/docker start <container>` - Start a container
  - `/docker stop <container>` - Stop a container
  - `/logs <container> [lines]` - View container logs
  - `/alerts` - Check container resource alerts

### Monitoring & Metrics
- **Resource Monitoring**
  - `/metrics` - Get current system metrics
  - Automated resource usage alerts
  - Prometheus & Grafana integration
  - Real-time container statistics

### Automated Alerting
- Configurable resource thresholds
- Automatic alert channel detection
- CPU and memory usage monitoring
- Real-time alert notifications

## Architecture

### Components
1. **Discord Bot (saturn_bot/)**
   - Command handling and user interaction
   - Asynchronous operation management
   - Error handling and response formatting

2. **Infrastructure Tools (saturn_bot/src/tools/)**
   - `aws_manager.py` - AWS infrastructure operations
   - `docker_manager.py` - Docker container management
   - `metrics_manager.py` - System metrics collection

3. **Monitoring Stack**
   - Prometheus for metrics collection
   - Grafana for visualization
   - Node Exporter for system metrics
   - Custom alert thresholds

### Directory Structure
```
saturn_bot/
├── src/
│   ├── bot/
│   │   └── saturn_bot.py
│   └── tools/
│       ├── aws_manager.py
│       ├── docker_manager.py
│       └── metrics_manager.py
├── docker/
│   ├── docker-compose.yml
│   └── prometheus/
│       └── prometheus.yml
└── terraform/
    └── ...
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose
- AWS Account and credentials
- Discord Bot Token

### Environment Variables
Create a `.env` file with:
```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_SERVER_ID=your_server_id

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
AWS_INSTANCE_ID=your_instance_id

# Docker Alert Thresholds (%)
DOCKER_ALERT_CPU_THRESHOLD=80
DOCKER_ALERT_MEMORY_THRESHOLD=80

# Prometheus URL (optional)
PROMETHEUS_URL=http://localhost:9090
```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd saturn-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the monitoring stack:
   ```bash
   cd saturn_bot/docker
   docker-compose up -d
   ```

4. Start the bot:
   ```bash
   python saturn_bot/src/bot/saturn_bot.py
   ```

## Usage Guide

### Basic Commands
1. Test AWS connectivity:
   ```
   /aws_test
   ```

2. Manage EC2 instance:
   ```
   /instance status
   /instance start
   /instance stop
   ```

3. View container status:
   ```
   /containers
   ```

4. Manage containers:
   ```
   /docker start container_name
   /docker stop container_name
   ```

5. View container logs:
   ```
   /logs container_name [number_of_lines]
   ```

### Monitoring
1. Check system metrics:
   ```
   /metrics
   ```

2. View alerts:
   ```
   /alerts
   ```

3. Access Grafana dashboard:
   - Open http://localhost:3000
   - Default credentials: admin/admin

## Error Handling

The bot includes comprehensive error handling:
- Command validation and synchronization
- AWS credential verification
- Docker operation monitoring
- Automatic alert channel fallback
- Message length management for logs

## Security Considerations

1. **Access Control**
   - Environment variable management
   - AWS credential security
   - Discord server-specific commands

2. **Resource Protection**
   - Container resource limits
   - Alert thresholds
   - Operation validation

## Maintenance

### Regular Tasks
1. Monitor alert thresholds
2. Review container resource usage
3. Check AWS resource utilization
4. Update dependencies
5. Review error logs

### Troubleshooting
- Check ActionLog.md for known issues and solutions
- Review bot console output for errors
- Verify environment variables
- Check Discord command synchronization

## Development

### Adding New Features
1. Create new tool in `src/tools/`
2. Add command handler in `saturn_bot.py`
3. Update documentation
4. Test thoroughly
5. Update ActionLog.md

### Testing
```bash
pytest tests/
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License
[Insert License Information]

## Support
- Check ToDoLog.md for planned features
- Review ActionLog.md for recent changes
- Submit issues for bugs or feature requests

## Roadmap
See ToDoLog.md for detailed development plans and future enhancements. 