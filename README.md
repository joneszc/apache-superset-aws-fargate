# Docker-compose for MXSDATA TEAM'S Apache Superset deployment 

### Overview
This Docker image is a modification of image from the official Superset DockerHub image (https://hub.docker.com/r/apache/superset) with additional features including an AWS RDS MySQL metastore db and gunicorn prod server for flask

# Running the docker stack for the first time:
Use:
`cd docker`

Use the following command to build the local images for initiating the AWS RDS MySQL db and testing Superset using the Flask development web server which is not intended to be used in production:

`docker-compose --file docker-compose-init-db.yml build`

`docker-compose --file docker-compose-init-db.yml up`

# Preparing images for production deployment using the gunicorn web server with gevent worker-class production usage:
Use:
`cd docker`

Use the following commands to build the local images to push to AWS ECR for ECS/Ec2 deployments and for immediate usage with `docker-compose up` command:

`docker-compose --file docker-compose.yml build`

`docker-compose --file docker-compose.yml up`

### Login Superset using Web UI
Open `http://localhost:8088` (or ec2 public DNS--edit env vars in docker-compose.env files) in your local browser, wait until you see the login page

