from app.core.config import s3_config
import boto3
import logging
from uuid import uuid4
from os.path import splitext
from fastapi import UploadFile

logger = logging.getLogger(__name__)



# Reusable S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=s3_config.AWS_ACCESS_KEY,
    aws_secret_access_key=s3_config.AWS_SECRET_KEY,
    region_name=s3_config.AWS_REGION,
)


def upload_file_to_s3(upload_file: UploadFile, s3_folder: str = "products") -> str:
    """Upload a file to S3 and return the CloudFront URL.

    Args:
        upload_file: FastAPI UploadFile object.
        s3_folder: Folder path inside the S3 bucket (e.g. 'products').

    Returns:
        The full CloudFront URL of the uploaded file.
    """
    try:
        file_extension = splitext(upload_file.filename)[1].lower()
        unique_filename = f"{uuid4()}{file_extension}"
        s3_key = f"{s3_folder}/{unique_filename}"

        upload_file.file.seek(0)

        s3_client.upload_fileobj(
            upload_file.file,
            s3_config.S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": upload_file.content_type or "application/octet-stream",
            },
        )

        cloudfront_url = f"https://{s3_config.CLOUDFRONT_DOMAIN}/{s3_key}"
        logger.info(f"Uploaded {upload_file.filename} → {cloudfront_url}")
        return cloudfront_url

    except Exception as e:
        logger.error(f"S3 upload failed for {upload_file.filename}: {str(e)}")
        raise e
    finally:
        upload_file.file.close()


def delete_file_from_s3(file_url: str) -> bool:
    """Delete a file from S3 using its CloudFront URL.

    Args:
        file_url: The full CloudFront URL of the file.

    Returns:
        True if deletion was successful, False otherwise.
    """
    try:
        # Extract S3 key from CloudFront URL
        # e.g. https://d7nsuxa5eflsu.cloudfront.net/products/abc.jpg → products/abc.jpg
        s3_key = file_url.replace(f"https://{s3_config.CLOUDFRONT_DOMAIN}/", "")

        s3_client.delete_object(
            Bucket=s3_config.S3_BUCKET_NAME,
            Key=s3_key,
        )

        logger.info(f"Deleted from S3: {s3_key}")
        return True

    except Exception as e:
        logger.error(f"S3 delete failed for {file_url}: {str(e)}")
        return False
