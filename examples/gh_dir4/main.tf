resource "aws_s3_bucket" "example" {
  bucket_prefix = "my-tf-test-bucket9"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}