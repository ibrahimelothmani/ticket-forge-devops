resource "aws_security_group" "rds_sg" {
  name        = "ticketforge-rds-sg"
  description = "Allow inbound traffic from EKS Cluster only"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL access from EKS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id] # الربط الأمني الصارم
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "postgres" {
  identifier           = "ticketforge-prod-db"
  allocated_storage    = 20
  max_allocated_storage = 100 # التوسع التلقائي عند زيادة مبيعات التذاكر
  db_name              = "ticketforge_db"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  username             = "ticketforge_admin"
  password             = var.db_password # يتم تمريره بأمان عبر السيكرتس
  skip_final_snapshot  = true

  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

variable "db_password" {
  type        = string
  description = "Database admin password"
  sensitive   = true
}