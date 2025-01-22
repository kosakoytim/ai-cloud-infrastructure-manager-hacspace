terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

module "ec2_instance" {
  source = "./modules/ec2"

  instance_name = "saturn-managed-instance"
  instance_type = "t2.micro"
  ami_id        = "ami-0c7217cdde317cfec"  # Amazon Linux 2023 AMI
} 