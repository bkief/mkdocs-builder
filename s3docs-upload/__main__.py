import os
import argparse
import glob
import mimetypes
from pathlib import Path

import boto3
from botocore import UNSIGNED as awsUNSIGNED
from botocore.client import Config as botoConfig
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(prog = 'S3Docs-Upload',
                    description = 'Uploads a MkDocs directory to a S3 bucket',
                    epilog = 'Requires env variables')

parser.add_argument('upload_path')
args = parser.parse_args()
upload_path = args.upload_path

ANON_MODE = False
S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_REGION')
S3_SERVER_PORT = os.environ.get('S3_SERVER_PORT')
S3_SERVER_PROTO = os.environ.get('S3_SERVER_PROTO')
S3_SERVER = os.environ.get('S3_SERVER')
S3_STYLE = os.environ.get('S3_STYLE')
S3_SSL_VERIFY = os.environ.get('S3_SSL_VERIFY')


if not S3_BUCKET_NAME:
    raise Exception("Environment variable 'S3_BUCKET_NAME' must be provided")
elif not S3_REGION:
    raise Exception("Environment variable 'S3_REGION' must be provided")
elif not S3_SERVER_PORT:
    raise Exception("Environment variable 'S3_SERVER_PORT' must be provided")
elif not S3_SERVER_PROTO:
    raise Exception("Environment variable 'S3_SERVER_PROTO' must be provided")
elif not S3_SERVER:
    raise Exception("Environment variable 'S3_SERVER' must be provided")
elif not S3_STYLE:
    raise Exception("Environment variable 'S3_STYLE' must be provided")

if S3_SSL_VERIFY.upper() == "FALSE":
  S3_SSL_VERIFY = False
else:
  S3_SSL_VERIFY = True

if not S3_ACCESS_KEY_ID and not S3_SECRET_KEY:
    ANON_MODE = True
elif S3_ACCESS_KEY_ID and not S3_SECRET_KEY:
    raise Exception(("Environment variable 'S3_SECRET_KEY' must be provided "
                     "when 'S3_ACCESS_KEY_ID' is provided"))
elif not S3_ACCESS_KEY_ID and S3_SECRET_KEY:
    raise Exception(("Environment variable 'S3_ACCESS_KEY_ID' must be provided "
                     "when 'S3_SECRET_KEY' is provided"))
else:
    ANON_MODE = False

if S3_STYLE.lower() not in ['path', 'virtual']:
    raise Exception(("Invalid 'S3_STYLE'. Should be 'path' or 'virtual', "
                     "but '%s' provided instead"%S3_STYLE))


end_point = f"{S3_SERVER_PROTO}://{S3_SERVER}:{S3_SERVER_PORT}"
print("Using %s S3 endpoint: "%(lambda am: 'anonymous' if am else '')(ANON_MODE), end_point) 

if ANON_MODE:
    s3_client = boto3.client('s3',
                              endpoint_url=end_point,
                              verify = S3_SSL_VERIFY,
                              region_name=S3_REGION,
                              config=botoConfig(s3={'addressing_style': S3_STYLE},
                                                signature_version=awsUNSIGNED,
                                                ),

                              )
else:
    s3_client = boto3.client('s3',
                              endpoint_url=end_point,
                               verify = S3_SSL_VERIFY,
                              region_name=S3_REGION,
                              aws_access_key_id=S3_ACCESS_KEY_ID,
                              aws_secret_access_key=S3_SECRET_KEY,
                              config=botoConfig(s3={'addressing_style': S3_STYLE},
                                                ),
                              )



obj_listing = s3_client.list_objects(Bucket=S3_BUCKET_NAME)
if 'Contents' in obj_listing:
    for o in obj_listing['Contents']:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=o['Key'])
    print('Bucket Emptied')
else:
    print('Bucket Already Empty')

os.chdir(upload_path)
for fpath in Path(".").rglob('*'):
    bn = os.path.basename(fpath)
    
    mimetype, _ = mimetypes.guess_type(fpath)
    if mimetype is None:
        mimetype = "application/octet-stream"
    try:
        response = s3_client.upload_file(fpath, S3_BUCKET_NAME, fpath, ExtraArgs={'ContentType': mimetype})
    except ClientError as e:
        print(e)
    
obj_listing = s3_client.list_objects(Bucket=S3_BUCKET_NAME)
if 'Contents' in obj_listing:
    for o in obj_listing['Contents']:
        print(o['Key'])

