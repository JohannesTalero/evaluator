resource "aws_security_group" "alb" {
  name_prefix = "${local.tag}-alb-"
  description = "ALB: HTTPS from internet"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.tag}-alb" }
  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTPS from internet"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "alb_all" {
  security_group_id = aws_security_group.alb.id
  description       = "All outbound to targets"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_security_group" "api" {
  name_prefix = "${local.tag}-api-"
  description = "API: traffic from ALB only"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.tag}-api" }
  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_ingress_rule" "api_from_alb" {
  security_group_id            = aws_security_group.api.id
  description                  = "From ALB on port 8000"
  from_port                    = 8000
  to_port                      = 8000
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.alb.id
}

resource "aws_vpc_security_group_egress_rule" "api_all" {
  security_group_id = aws_security_group.api.id
  description       = "Outbound to SQS, RDS, S3"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_security_group" "workers" {
  name_prefix = "${local.tag}-workers-"
  description = "Workers: outbound only (SQS, S3, AI provider)"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.tag}-workers" }
  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_egress_rule" "workers_all" {
  security_group_id = aws_security_group.workers.id
  description       = "Outbound to SQS, S3, AI provider"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_security_group" "rds" {
  name_prefix = "${local.tag}-rds-"
  description = "RDS: PostgreSQL from API and workers"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.tag}-rds" }
  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_api" {
  security_group_id            = aws_security_group.rds.id
  description                  = "PostgreSQL from API"
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.api.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_workers" {
  security_group_id            = aws_security_group.rds.id
  description                  = "PostgreSQL from workers"
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.workers.id
}

resource "aws_vpc_security_group_egress_rule" "rds_all" {
  security_group_id = aws_security_group.rds.id
  description       = "Outbound"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
