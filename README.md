# API Documentation
# Table of Contents
- [API Documentation](#api-documentation)
- [Table of Contents](#table-of-contents)
  - [How to Test the API](#how-to-test-the-api)
  - [Requirements Analysis](#requirements-analysis)
  - [Project Structure](#project-structure)
  - [Running Locally](#running-locally)
  - [Architecture Justification](#architecture-justification)
    - [Why Docker on EC2?](#why-docker-on-ec2)
    - [Why Gmail SMTP?](#why-gmail-smtp)
    - [Advantages of This Architecture:](#advantages-of-this-architecture)
## How to Test the API

To test the API on the deployed page, follow these steps:

1. **Authentication**: 
   - You need to authenticate using the `/login` endpoint, which will return an `access_token` and a `refresh_token`.
   - The `access_token` is valid for only 5 minutes. After it expires, you can use the `refresh_token` to request a new `access_token` by calling the `/refresh_token` endpoint.
   - Use the following credentials to log in:
     - **Username**: `AdminGR`
     - **Password**: `admin`

2. **Authorization**: 
   - Once you have the `access_token`, include it in the `Authorization` header as follows:
     ```
     Bearer <access_token>
     ```
   - After authorization, you can access the endpoints that require authentication.

## Requirements Analysis

Before starting development, a requirements analysis was made. The requirements are documented in the `documentation` folder in a Markdown file called file called [`SRS.md`](./documentation/SRS.md). This file contains:
- Objective
- Scope
- Functional requirements
- Architectural design
- Non-functional requirements

## Project Structure

The project is structured as follows:

- **`server/`**: This folder contains the core Django project.
  - **`api/`**: This is the Django app within the project.
    - **`views.py`**: Contains the logic for each endpoint (controller).
    - **`models.py`**: Defines the models used in the project.
    - **`serializers.py`**: Includes validation and functions for the models.
    - **`tests.py`**: Contains unit tests for each endpoint.
  - **`urls.py`**: Defines the routes for all endpoints within the project.
  - **`settings.py`**: Holds all project configurations.

## Running Locally

To run the project locally:

1. **Docker Setup**: 
   - Run the following command to start the services:
     ```bash
     docker-compose up --build
     ```
   - This will build and start all necessary containers.
   - To run the services in the background (detached mode), use:
     ```bash
     docker-compose up -d
     ```

2. **Stopping the services**:
   - When you're done and want to stop the services, run:
     ```bash
     docker-compose down
     ```

3. **Environment Variables**: 
   - Ensure that your environment variables are set properly. However, note that the `.env` file is not included in the repository for security reasons.

## Architecture Justification

The project uses the following architecture:

- **Amazon EC2**: The project is deployed on an EC2 instance, and the application is containerized within Docker. This ensures consistency across different environments and simplifies deployment.
  
- **Django**: The framework is used for developing the API, offering a clean and efficient development process.
- **PostgreSQL**: Relatinal database that it is well-suited for storing structured data.
  
- **Amazon RDS**: Used for database management, providing scalability, reliability, and easy maintenance of the database.
  
- **Gmail SMTP**: Used for email services since a domain was not available to configure AWS SES.

### Why Docker on EC2?

Containerizing the application inside Docker on EC2 has several benefits:
- **Consistency**: Ensures the application runs the same across different environments (local, development, production).
- **Isolation**: Docker isolates the app and its dependencies, preventing conflicts with other system services.
- **Scalability**: With EC2, we can easily scale the application as needed, and Docker provides a lightweight, resource-efficient solution to manage the application.

### Why Gmail SMTP?

Gmail was used due to the absence of a dedicated domain, which is required to set up Amazon SES for sending emails. While Gmail is sufficient for testing purposes, AWS SES could be implemented for production if a domain becomes available.

### Advantages of This Architecture:
- **Scalability**: The architecture is built to scale, with AWS EC2 handling traffic growth and Amazon RDS ensuring the database can expand as needed. The use of Docker further ensures flexibility in managing application instances.
- **Cost-Effectiveness**: Using cloud services like AWS ensures you only pay for what you use, allowing for flexible scaling without unnecessary costs.
- **Security**: Environment variables and authentication tokens ensure secure communication between the client and server. Docker also adds an additional layer of isolation, improving security.

For more details of the architecture review the "Architecture Design" section in  [`SRS.md`](./documentation/SRS.md).