resource "aws_s3_bucket" "example" {
  bucket_prefix = "my-tf-test-bucket7"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}