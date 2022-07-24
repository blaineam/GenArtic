# GenArtic
A Simple Text to Image Generation As a Docker Web Service

# Requirements
- A S3 Compatible Storage Provider
- A SMTP Service Provider
- A Docker host with a CUDA 11 GPU with at least 16GB of VRAM (Tested on a 24GB 3090 Ti)

# SETUP
- copy `dotenv.example` to `.env`
- Fill out detail in .env with an S3 compatible storage provider and an SMTP Service provider of your choice
- Run `docker compose up -d`
- Open browser to http://localhost:8873 and run a prompt

# Known Issues
- On occasion the UI fails to display the result but the emails still send a link to them
- Running a prompt without enough VRAM will fail
- DIFFVG still needs to add CUDA 11 support to fix the pixel, clip draw, and line drawing modes
- S3 bucket currently needs to be public
- Nothing cleans up previous generated images
- still trying to publish image to docker hub
