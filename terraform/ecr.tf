# قائمة الخدمات التي نريد إنشاء مستودعات لها
variable "services" {
  type    = list(string)
  default = ["api-gateway", "ticket-service", "payment-service", "notification-service"]
}

# إنشاء المستودعات ديناميكياً باستخدام loop
resource "aws_ecr_repository" "microservices_ecr" {
  for_each             = toset(var.services)
  name                 = "ticketforge/${each.value}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    # فحص أمني تلقائي فور عمل Push للـ Image (مبدأ DevSecOps)
    scan_on_push = true
  }

  encryption_configuration {
    # تشفير الصور المخزنة باستخدام AWS KMS لحمايتها
    encryption_type = "KMS"
  }
}

# طباعة الـ URLs الخاصة بالمستودعات بعد البناء لاستعمالها في الـ Pipeline
output "ecr_repository_urls" {
  value = { for k, v in aws_ecr_repository.microservices_ecr : k => v.repository_url }
}