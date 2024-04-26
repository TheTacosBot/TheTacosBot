module "vpc" {
  source = "cloudposse/vpc/aws"
  # Cloud Posse recommends pinning every module to a specific version
  # version     = "x.x.x"
  namespace = "eg"
  stage     = "test"
  name      = "app"

  ipv4_primary_cidr_block = "10.1.0.0/16"

  assign_generated_ipv6_cidr_block = false
}

module "dynamic_subnets" {
  source = "cloudposse/dynamic-subnets/aws"
  # Cloud Posse recommends pinning every module to a specific version
  # version     = "x.x.x"
  namespace          = "eg"
  stage              = "test"
  name               = "app"
  availability_zones = ["us-west-2a","us-west-2b","us-west-2c"]
  vpc_id             = module.vpc.vpc_id
  igw_id             = [module.vpc.igw_id]
  ipv4_cidr_block         = ["10.0.0.0/16"]
}