terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags { tags = { Project = "evaluator", Environment = "dev", ManagedBy = "terraform" } }
}

module "networking" {
  source      = "../../modules/networking"
  project     = "evaluator"
  environment = "dev"
  vpc_cidr    = "10.0.0.0/16"
}
