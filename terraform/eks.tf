module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "ticketforge-prod-cluster"
  cluster_version = "1.28"

  cluster_endpoint_public_access  = true # للسماح لك بإدارته من حاسوبك محلياً

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets

  # إعداد السيرفرات التشغيلية (Worker Nodes)
  eks_managed_node_groups = {
    general = {
      min_size     = 1
      max_size     = 5
      desired_size = 2 # نبدأ بسيرفرين لتوزيع الحمل عبر الـ AZs

      instance_types = ["t3.medium"] # حجم ممتاز وموفر ويتحمل الـ Virtual Threads والمراقبة
      capacity_type  = "ON_DEMAND"
    }
  }
}