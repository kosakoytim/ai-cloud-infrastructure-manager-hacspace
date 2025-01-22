A Discord bot for managing AWS cloud infrastructure with Terraform integration. This bot allows you to manage EC2 instances through Discord commands while maintaining infrastructure as code using Terraform.

## Current Features

### Discord Bot Commands
- `/aws_test` - Test AWS connectivity and verify instance access
- `/instance action:status` - Get detailed instance status including:
  - Instance state with visual indicators
  - Public IP address (when running)
  - Instance type and launch time
  - SSH connection details
  - Instance tags
- `/instance action:start` - Start the EC2 instance with progress tracking
- `/instance action:stop` - Stop the EC2 instance with progress tracking

### Infrastructure (Terraform)
- EC2 instance management:
  - Instance type: t2.micro
  - OS: Ubuntu 22.04 LTS
  - Automatic public IP assignment
  - Instance tagging
- Security:
  - Dedicated security group
  - SSH access (port 22)
  - Secure key pair management
- Infrastructure as Code:
  - Modular Terraform configuration
  - State management
  - Resource tagging

## Project Structure
```
.
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                # Main Terraform configuration
│   ├── provider.tf            # AWS provider configuration
│   ├── outputs.tf             # Terraform outputs
│   ├── saturn-key            # SSH private key (keep secure!)
│   ├── saturn-key.pub        # SSH public key
│   └── modules/
│       └── ec2/              # EC2 instance module
│           ├── main.tf       # Instance and security group
│           ├── variables.tf  # Module variables
│           └── outputs.tf    # Module outputs
├── saturn_bot/                # Discord Bot
│   └── src/
│       ├── bot/
│       │   └── saturn_bot.py # Discord bot implementation
│       └── tools/
│           └── aws_manager.py # AWS management tools
└── .env                      # Environment variables
```

## Setup and Configuration

### Prerequisites
- Python 3.8 or higher
- Terraform
- AWS Account
- Discord Bot Token

### Environment Variables
Required variables in `.env`:
```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
export AWS_INSTANCE_ID=your_instance_id

# Discord Configuration
export DISCORD_BOT_TOKEN=your_bot_token
export DISCORD_SERVER_ID=your_server_id
```

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```
4. Create infrastructure:
   ```bash
   terraform apply
   ```
5. Start the Discord bot:
   ```bash
   python saturn_bot/src/bot/saturn_bot.py
   ```

### SSH Access
Connect to the instance:
```bash
ssh -i terraform/saturn-key ubuntu@<instance_ip>
```
- Username: `ubuntu`
- Key location: `terraform/saturn-key`
- Required permissions: `chmod 400 terraform/saturn-key`

## Error Handling
The bot includes comprehensive error handling:
- AWS credential validation
- Instance state verification
- Command execution monitoring
- Detailed error messages
- Automatic retry logic for state changes

## Potential Improvements

### Discord Bot
1. Additional Instance Commands
   - Instance reboot
   - Instance termination
   - New instance creation
   - Multiple instance management

2. Enhanced Status Information
   - Resource utilization metrics
   - Cost estimation
   - CloudWatch alarms integration
   - Automated status reporting

3. Monitoring Features
   - Real-time CPU/Memory monitoring
   - Network traffic analysis
   - Cost tracking and budgeting
   - Custom alert thresholds

4. Security Enhancements
   - Discord role-based access
   - Command audit logging
   - Action confirmation prompts
   - Rate limiting

### Infrastructure
1. Advanced Resources
   - Custom VPC configuration
   - Load balancer setup
   - Auto-scaling implementation
   - Database integration

2. Security Improvements
   - Private subnet deployment
   - Bastion host configuration
   - Security group refinement
   - IAM role optimization

3. Backup and Recovery
   - Automated EBS snapshots
   - AMI backup strategy
   - Disaster recovery planning
   - Cross-region replication

4. Cost Management
   - Resource scheduling
   - Instance size optimization
   - Cost allocation tagging
   - Budget alerts

## Maintenance

### Regular Tasks
1. Code Maintenance
   - Update dependencies
   - Review security patches
   - Optimize performance
   - Update documentation

2. Infrastructure Updates
   - Review security groups
   - Update AMI versions
   - Check for cost optimizations
   - Validate backups

### Best Practices
1. Security
   - Rotate AWS credentials
   - Update security groups
   - Monitor access logs
   - Review permissions

2. Cost Management
   - Monitor usage patterns
   - Right-size instances
   - Review unused resources
   - Set up cost alerts

## Contributing
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests if applicable
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 