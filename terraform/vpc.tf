module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "ticketforge-prod-vpc"
  cidr = "10.0.0.0/16"

  # التوزيع عبر منطقتي توافر لضمان الـ High Availability
  azs             = ["eu-west-1a", "eu-west-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"] # للـ EKS Pods والـ Compute
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"] # للـ ALB والمنافذ الخارجية
  database_subnets = ["10.0.201.0/24", "10.0.202.0/24"] # لعزل الـ RDS والبيانات

  enable_nat_gateway = true
  single_nat_gateway = true # لتوفير التكلفة في البداية، في الإنتاج الفعلي نجعلها false

  enable_vpn_gateway = false

  # وسوم حيوية لكي يتعرف AWS EKS على الـ Subnets ويحكم فيها الـ Load Balancers تلقائياً
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}