resource "aws_s3_bucket" "example" {
  bucket_prefix = "my-tf-test-bucket3"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}