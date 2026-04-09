# Technical Specification Document for Consistency Tracker Project

## 1. Overview
This document outlines the technical specifications for the Consistency Tracker project. It includes details about the system architecture, data models, API specifications, LLM integration guide, database schema, authentication strategy, and deployment instructions.

## 2. System Architecture
- **Architecture Type**: Microservices
- **Technology Stack**: 
  - Backend: Node.js, Express
  - Frontend: React
  - Database: PostgreSQL
  - Message Queue: RabbitMQ
- **Components**:
  - User Service: Manages user authentication and profiles.
  - Consistency Service: Handles tracking and analytics services.
  - Notification Service: Manages alerts and notifications.

## 3. Data Models
### User
- **Attributes**:
  - `id`: UUID (Primary Key)
  - `username`: String
  - `email`: String
  - `passwordHash`: String
  - `created_at`: Timestamp

### ConsistencyRecord
- **Attributes**:
  - `id`: UUID (Primary Key)
  - `userId`: UUID (Foreign Key)
  - `value`: Float
  - `timestamp`: Timestamp

## 4. API Specifications
### Authentication
- **Endpoint**: `/api/auth/login`
  - **Method**: POST
  - **Body**:
    ```json
    {
      "email": "string",
      "password": "string"
    }
    ```

- **Response**:
  - **Status 200**:
    ```json
    {
      "token": "jwt_token"
    }
    ```

### ConsistencyTracking
- **Endpoint**: `/api/consistency`
  - **Method**: POST
  - **Body**:
    ```json
    {
      "value": float
    }
    ```

- **Response**:
  - **Status 201**
    ```json
    {
      "message": "Record created successfully"
    }
    ```

## 5. LLM Integration Guide
The system integrates with an LLM to analyze user consistency records. This integration is achieved using the following steps:
1. **Data Preparation**: Clean and format the consistency data.
2. **Model Training**: Train the LLM with the prepared data.
3. **Inferences**: Use the model to provide insights on user consistency.

## 6. Database Schema
- **User Table**: Store user information.
- **ConsistencyRecord Table**: Store records of user consistency data.

## 7. Authentication Strategy
- Utilizes JWT (JSON Web Tokens) for session management. Tokens are issued upon successful login and are required for accessing protected API endpoints.

## 8. Deployment Instructions
1. **Environment Setup**:
   - Install Docker and Docker Compose.
2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   ```
3. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```
4. **Access the application** at `http://localhost:3000`.

---

## Author
- **Name**: Naveen CSD-13677
- **Date**: 2026-04-09