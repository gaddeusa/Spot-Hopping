# 3. Launch Template
resource "aws_launch_template" "spot_template" {
  name_prefix   = "spot-hopping-template"
  image_id      = "ami-0230bd60aa48260c6" # Amazon Linux 2023 (us-east-1)
  instance_type = "t3.micro"

  iam_instance_profile {
    name = aws_iam_instance_profile.spot_profile.name
  }

  user_data = filebase64("${path.module}/../../scripts/user_data.sh")

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "Spot-Hopping-Worker"
    }
  }
}

# 4. Spot Fleet (via ASG)
resource "aws_autoscaling_group" "spot_fleet" {
  desired_capacity    = 1
  max_size            = 1
  min_size            = 0
  vpc_zone_identifier = ["subnet-xyz"] # REPLACE with your Subnet ID

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.spot_template.id
        version            = "$Latest"
      }

      override {
        instance_type = "t3.micro"
      }
      override {
        instance_type = "t3a.micro"
      }
    }

    instances_distribution {
      on_demand_base_capacity                  = 0
      on_demand_percentage_above_base_capacity = 0 # 100% Spot
      spot_allocation_strategy                 = "price-capacity-optimized"
    }
  }
}
