from fastapi import FastAPI, File, UploadFile
import boto3
from botocore.exceptions import NoCredentialsError
import uuid

app = FastAPI()

# AWS configuration
S3_BUCKET = "image-upload-demo-bucket"
DYNAMO_TABLE = "ImageMetadata"
REGION = "ap-south-1"  # change to your AWS region

# Initialize clients
s3 = boto3.client("s3", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMO_TABLE)

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI Image Upload Service"}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Generate unique file name
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}_{file.filename}"

        # Upload to S3
        s3.upload_fileobj(file.file, S3_BUCKET, file_name)

        # Store metadata in DynamoDB
        table.put_item(Item={
            "ImageID": file_id,
            "FileName": file_name,
            "Bucket": S3_BUCKET
        })

        return {"status": "success", "file_name": file_name}

    except NoCredentialsError:
        return {"error": "AWS credentials not found"}
    except Exception as e:
        return {"error": str(e)}
