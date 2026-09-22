import pandas as pd
import boto3
import os
from google.cloud import storage

def extract_data_from_s3(bucket_name, file_key):
    print(f"Starting extraction from S3: bucket={bucket_name}, key={file_key}")
    s3_renamed = boto3.client('s3')
    try:
        s3_renamed.download_file(bucket_name, file_key, 'local_data.csv')
        print("Data extracted successfully.")
    except Exception as e:
        print(f"Error during extraction: {e}")

def extract_data_from_gcs(bucket_name, file_key):
    print(f"Starting extraction from Google Cloud Storage: bucket={bucket_name}, key={file_key}")
    client = storage.Client()
    try:
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(file_key)
        blob.download_to_filename('local_data.csv')
        print("Data extracted successfully.")
    except Exception as e:
        print(f"Error during extraction: {e}")

def transform_data():
    print("Starting transformation of data.")
    try:
        data = pd.read_csv('local_data.csv')
        # Example transformation: dropping NA values
        transformed_data = data.dropna()
        print("Data transformed successfully.")
        return transformed_data
    except Exception as e:
        print(f"Error during transformation: {e}")
        return None

def load_data_to_s3(transformed_data, bucket_name, output_key):
    print(f"Starting loading to S3: bucket={bucket_name}, key={output_key}")
    try:
        transformed_data.to_csv('transformed_data.csv', index=False)
        s3_renamed = boto3.client('s3')
        s3_renamed.upload_file('transformed_data.csv', bucket_name, output_key)
        print("Data loaded to S3 successfully.")
    except Exception as e:
        print(f"Error during loading to S3: {e}")

def load_data_to_gcs(transformed_data, bucket_name, output_key):
    print(f"Starting loading to Google Cloud Storage: bucket={bucket_name}, key={output_key}")
    try:
        transformed_data.to_csv('transformed_data.csv', index=False)
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(output_key)
        blob.upload_from_filename('transformed_data.csv')
        print("Data loaded to Google Cloud Storage successfully.")
    except Exception as e:
        print(f"Error during loading to Google Cloud Storage: {e}")

def main():
    cloud_service = 's3'  # or 'gcs'
    if cloud_service == 's3':
        bucket_name = 'your-s3-bucket'
        file_key = 'data/input_data.csv'
        output_key = 'data/output_data.csv'

        extract_data_from_s3(bucket_name, file_key)
        transformed_data = transform_data()
        if transformed_data is not None:
            load_data_to_s3(transformed_data, bucket_name, output_key)

    elif cloud_service == 'gcs':
        bucket_name = 'your-gcs-bucket'
        file_key = 'data/input_data.csv'
        output_key = 'data/output_data.csv'

        extract_data_from_gcs(bucket_name, file_key)
        transformed_data = transform_data()
        if transformed_data is not None:
            load_data_to_gcs(transformed_data, bucket_name, output_key)

if __name__ == "__main__":
    main()
