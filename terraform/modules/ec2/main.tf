resource "aws_key_pair" "instance_key" {
  key_name   = "saturn-key"
  public_key = file("${path.root}/saturn-key.pub")
}

resource "aws_security_group" "instance_sg" {
  name_prefix = "saturn-instance-sg"
  description = "Security group for Saturn-managed EC2 instance"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "saturn-instance-sg"
  }
}

resource "aws_instance" "main" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.instance_key.key_name

  vpc_security_group_ids = [aws_security_group.instance_sg.id]

  tags = {
    Name = var.instance_name
  }
} 