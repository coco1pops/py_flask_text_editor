#!/bin/bash

if [ -f ~/tag.sh ]; then
  source ~/tag.sh
else
  TAG=1
fi
printf -v PTAG "%05d" "$TAG"

# Exit immediately if a .env file is not found
if [ ! -f .env ]; then
    echo "Error: .env file not found in the current directory."
    exit 1
fi

# Load variables from .env into the current shell environment
export $(grep -v '^#' .env | xargs)

# Check if the necessary variables are set
if [ -z "$FLASK_DB_USER" ] || [ -z "$FLASK_DB_PASSWORD" ] || [ -z "$FLASK_DB_NAME" ]; then
    echo "Error: Not all required PostgreSQL environment variables are set in .env"
    exit 1
fi

if [ -z "$ENVIRONMENT" ]; then 
   echo "Error: Environment not set"
   exit 1
fi

# Construct the --build-arg arguments
BUILD_ARGS=""
BUILD_ARGS="${BUILD_ARGS} --set-env-vars FLASK_DB_USER=${FLASK_DB_USER}"
BUILD_ARGS="${BUILD_ARGS},FLASK_DB_PASSWORD=${FLASK_DB_PASSWORD}"
BUILD_ARGS="${BUILD_ARGS},FLASK_DB_NAME=${FLASK_DB_NAME}"
BUILD_ARGS="${BUILD_ARGS},ENVIRONMENT=${ENVIRONMENT}" 
BUILD_ARGS="${BUILD_ARGS},INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME}"
BUILD_ARGS="${BUILD_ARGS},SERVICE_ACCOUNT_FILE_PATH=${SERVICE_ACCOUNT_FILE_PATH}"
BUILD_ARGS="${BUILD_ARGS},FLASK_SECRET_KEY=${FLASK_SECRET_KEY}"  

echo "Starting deployment with build arguments:"
echo $BUILD_ARGS

gcloud run deploy editorapp \
  --source . \
  --add-cloudsql-instances story-writer-469107:us-east1:editordb \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  $BUILD_ARGS

#  --add-cloudsql-instances story-writer-469107:us-east1:editordb \

echo "Updating TAG"
TAG=$((TAG+1))
echo "TAG=$TAG">~/tag.sh
