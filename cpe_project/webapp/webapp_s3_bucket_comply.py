#!/usr/bin/env python3

"""
https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html
Coverages for
[S3.1] S3 Block Public Access setting should be enabled
[S3.4] S3 buckets should have server-side encryption enabled
[S3.8] S3 Block Public Access setting should be enabled at the bucket-level
[S3.9] S3 bucket server access logging should be enabled
[S3.14] S3 buckets should use versioning

"""

import boto3
from botocore.exceptions import ClientError
from flask import Flask, render_template, request
from markupsafe import Markup

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
INDEX_TEMPLATE = 'index.html'

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    index function
    """
    if request.method == 'POST':
        # Get form data
        bucket_name = request.form['bucket']
        profile_name = request.form['profile']

        # Set up boto3 client
        session = boto3.Session(profile_name=profile_name)
        s3_client = session.client('s3')

        # Check bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            msg = f'{bucket_name}: Bucket exists.'
        except ClientError as error:
            if error.response['Error']['Code'] == '404':
                msg = f"Bucket {bucket_name} doesn't exist."
            elif error.response['Error']['Code'] == '403':
                msg = f"Access denied to bucket {bucket_name}."
            else:
                raise
            return render_template(INDEX_TEMPLATE, message=msg)

        # Process S3 operations
        s3_operations = [
            {'name': '[S3.1] Block public access',
             'method': s3_client.put_public_access_block,
             'params': {
                 'Bucket': bucket_name,
                 'PublicAccessBlockConfiguration': {
                     'BlockPublicAcls': True,
                     'IgnorePublicAcls': True,
                     'BlockPublicPolicy': True,
                     'RestrictPublicBuckets': True
                 }
             }},
            {'name': '[S3.4] Enable server-side encryption',
             'method': s3_client.put_bucket_encryption,
             'params': {
                 'Bucket': bucket_name,
                 'ServerSideEncryptionConfiguration': {
                     'Rules': [
                         {
                             'ApplyServerSideEncryptionByDefault': {
                                 'SSEAlgorithm': 'AES256'
                             }
                         }
                     ]
                 }
             }},
            {'name': '[S3.9] Enable bucket logging',
             'method': s3_client.put_bucket_logging,
             'params': {
                 'Bucket': bucket_name,
                 'BucketLoggingStatus': {
                     'LoggingEnabled': {
                         'TargetBucket': bucket_name,
                         'TargetPrefix': 'logs/'
                     }
                 }
             }},
            {'name': '[S3.14] Enable bucket versioning',
             'method': s3_client.put_bucket_versioning,
             'params': {
                 'Bucket': bucket_name,
                 'VersioningConfiguration': {
                     'Status': 'Enabled'
                 }
             }},
            {'name': 'Set tags',
             'method': s3_client.put_bucket_tagging,
             'params': {
                 'Bucket': bucket_name,
                 'Tagging': {
                     'TagSet': [
                         {'Key': 'Category', 'Value': 'DevOps'},
                         {'Key': 'Product', 'Value': 'S3 Bucket'}
                     ]
                 }
             }},
        ]

        # Perform S3 operations
        msg = ''
        for operation in s3_operations:
            try:
                operation['method'](**operation['params'])
                msg += Markup(f"{bucket_name}: {operation['name']} enabled.<br>")
            except ClientError as error:
                msg += f"Failed to enable {operation['name']}: {error}<br>"

        return render_template(INDEX_TEMPLATE, message=msg)

    return render_template(INDEX_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
