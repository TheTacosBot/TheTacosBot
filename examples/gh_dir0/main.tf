resource "aws_s3_bucket" "example" {
  bucket_prefix = "my-tf-test-bucket4"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}