#!/bin/bash

# Exit immediately if a .env file is not found
if [ ! -f .env ]; then
    echo "Error: .env file not found in the current directory."
    exit 1
fi

# Load variables from .env into the current shell environment
export $(grep -v '^#' .env | xargs)

# Check if the necessary variables are set
if [ -z "$FLASK_DB_USER" ] || [ -z "$FLASK_DB_PASSWORD" ] || [ -z "$FLASK_DB_HOST" ] || [ -z "$FLASK_DB_NAME" ]; then
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
BUILD_ARGS="${BUILD_ARGS} --set-env-vars FLASK_DB_PASSWORD=${FLASK_DB_PASSWORD}"
BUILD_ARGS="${BUILD_ARGS} --set-env-vars FLASK_DB_HOST=${FLASK_DB_HOST}"
BUILD_ARGS="${BUILD_ARGS} --set-env-vars FLASK_DB_PORT=${FLASK_DB_PORT}"
BUILD_ARGS="${BUILD_ARGS} --set-env-vars FLASK_DB_NAME=${FLASK_DB_NAME}"
BUILD_ARGS="${BUILD_ARGS} --set-env-vars ENVIRONMENT=${ENVIRONMENT}" 
BUILD_ARGS="${BUILD_ARGS} --set-env-vars CLOUD_SQL_CONNECTION_NAME=${CLOUD_SQL_CONNECTION_NAME}" 

echo "Starting gcloud beta code dev with build arguments:"
echo $BUILD_ARGS
#gcloud beta code dev --source=. $BUILD_ARGS
gcloud run deploy editor \
  --image europe-west4-docker.pkg.dev/big-pact-460610-j7/cloud-run-source-deploy/editor:123456 \
  --platform managed \
  --region europe-west4 \
  --allow-unauthenticated \
  --add-cloudsql-instances big-pact-460610-j7:europe-west4:editor\
  $BUILD_ARGS
