terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # لتخزين الـ State بشكل آمن في السحاب (يمكن تفعيله لاحقاً بإنشاء S3 Bucket)
  # backend "s3" {
  #   bucket = "future-eagle-terraform-state"
  #   key    = "prod/ticketforge/terraform.tfstate"
  #   region = "eu-west-1"
  # }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = "Production"
      Project     = "TicketForge"
      ManagedBy   = "Terraform"
    }
  }
}

variable "aws_region" {
  default = "eu-west-1" # اخترنا زون إيرلندا القريبة والمستقرة
}