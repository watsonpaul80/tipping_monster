import os
import boto3


def download_if_missing(bucket: str, key: str, dest_path: str) -> str:
    """Download a file from S3 to dest_path if it does not already exist.

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket.
    key : str
        The object key within the bucket.
    dest_path : str
        Local filesystem path where the file should be stored.

    Returns
    -------
    str
        The path to the downloaded (or existing) file.
    """
    if os.path.exists(dest_path):
        return dest_path

    print(f"Downloading {key} from s3://{bucket} to {dest_path}")
    s3 = boto3.client("s3")
    s3.download_file(bucket, key, dest_path)
    return dest_path
