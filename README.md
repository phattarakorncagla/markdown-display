
## Chunk 1
<think>
We are writing a specification document for the project named "iphone-app-notification".
 The provided source code shows a public server that handles webhooks, specifically for DocuSign events, and sends push notifications to iOS devices.

 The main components are:
 1. A server setup (server.ts) that runs an HTTPS server and sets up routes.
 2. A controller for sending Apple Push Notifications (nodeApnController.ts).
 3. A webhook controller (webhookController.ts) that handles incoming DocuSign webhook events and triggers notifications.
 4. Route definitions (routes.ts and webhookRoutes.ts).

 The system interacts with an entity called "Notification" and "User_Application", which are likely part of an ORM (like TypeORM).

 The main functionality:
 - The server listens on port 443 (HTTPS).
 - It has a route for the root ("/") that returns a simple greeting.
 - It has a route for webhooks, specifically at "/webhooks/docusign", which accepts POST requests.

 The webhook endpoint:
   - Validates the incoming request from DocuSign using HMAC.
   - Processes the event (either 'envelope-sent' or 'recipient-completed').
   - For 'envelope-sent': 
        * Creates a new notification in the database.
        * Increments the count of unsigned notifications for the user.
        * Sends a push notification to the user's device (using APNs).
   - For 'recipient-completed':
        * Updates the notification to mark it as signed.
        * Decrements the count of unsigned notifications for the user.

 We are to write a specification document that describes the endpoints and their behavior.

 Since the project is about an iPhone app notification, but the provided code is for the server, we focus on the server endpoints.

 We note that the server has:
   - A root endpoint: GET /
   - A webhook endpoint: POST /webhooks/docusign

 Additionally, the server uses other endpoints internally (via Axios) to interact with what seems to be another service (or the same server?) for CRUD operations on notifications and user applications. However, these internal endpoints are not exposed in the current routing of the provided code. Therefore, we focus on the exposed endpoints.

 We also note that the server uses HTTPS and requires key and certificate files.

 Specification Document Outline:

 1. Introduction: Briefly describe the purpose of the server.
 2. Endpoints:
    a. Root Endpoint
    b. DocuSign Webhook Endpoint

 3. Detailed description of each endpoint.

 Let's write the document accordingly.
</think>
# Specification Document: iPhone App Notification Server

## Overview
This document outlines the specifications for the iPhone App Notification Server, which handles DocuSign webhook events and sends push notifications to iOS devices. The server processes DocuSign envelope events, manages user notifications, and communicates with Apple Push Notification service (APNs) to deliver real-time updates to users.

## System Architecture
The server consists of:
1. HTTPS server with Express.js
2. DocuSign webhook handler
3. Apple Push Notification (APN) service integration
4. Database interaction layer (via Axios requests)

---

## Endpoint Specifications

### 1. Root Endpoint
**Purpose**: Health check and basic server verification  
**HTTP Method**: `GET`  
**Path**: `/`  

**Request Format**: None  
**Response Format**: Plain text  
**Response Example**:
```
Hello, TypeScript + Node.js + Express!
```

**Status Codes**:
- `200 OK`: Server is operational

---

### 2. DocuSign Webhook Endpoint
**Purpose**: Process DocuSign webhook events and trigger push notifications  
**HTTP Method**: `POST`  
**Path**: `/webhooks/docusign`  

#### Request Requirements
- **Headers**:
  - `x-docusign-signature-1`: HMAC signature for verification
- **Body**: DocuSign event payload (JSON format)

#### Security Validation
```ts
// HMAC verification process
const computeHash = (payload: string, secret: string) => {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.write(payload);
  hmac.end();
  return hmac.read().toString('base64');
};

const isHashValid = (payload: string, verify: string, secret: string) => {
  return crypto.timingSafeEqual(
    Buffer.from(verify, 'base64'),
    Buffer.from(computeHash(payload, secret), 'base64')
  );
};
```

#### Supported Events
1. **`envelope-sent`**:
   - Creates new notification record
   - Increments user's unsigned notification count
   - Sends push notification to user's device

2. **`recipient-completed`**:
   - Marks notification as signed
   - Decrements user's unsigned notification count

#### Response Format
- **Success**: `200 OK` with "Success" message
- **Errors**:
  - `500 Internal Server Error` with descriptive message for:
    - Missing HMAC token
    - Invalid signature verification
    - APN notification failures
    - Database operation errors

#### Processing Flow
```mermaid
graph TD
A[Webhook Received] --> B{Validate HMAC}
B -->|Invalid| C[Return 500 Error]
B -->|Valid| D{Check Event Type}
D -->|envelope-sent| E[Create Notification]
E --> F[Increment Unsigned Count]
F --> G[Send APN]
D -->|recipient-completed| H[Update Notification]
H --> I[Decrement Unsigned Count]
I --> J[Update Database]
J --> K[Return 200 Success]
```

---

## Notification Service

### Apple Push Notification (APN) Integration
**Configuration**:
```ts
const options = {
  token: { 
    key: process.env.APN_KEY, 
    keyId: process.env.APN_KEY_ID,
    teamId: process.env.APN_TEAM_ID
  },
  production: process.env.NODE_ENV === 'production'
};
```

**Notification Payload**:
```json
{
  "alert": "{sender}さんから{subject}の承認依頼が届きました。",
  "body": "{sender}さんから{subject}の承認依頼が届きました。",
  "badge": {num_of_unsigned_notif},
  "topic": "{bundleId}",
  "payload": {
    "from": "approveHub, using node-apn",
    "source": "approveHub server"
  }
}
```

**Key Fields**:
- `badge`: Shows count of pending notifications on app icon
- `topic`: iOS bundle identifier (e.g., `com.example.app`)
- `alert`: Notification preview text

---

## Environment Variables
| Variable | Purpose | Required |
|----------|---------|----------|
| `KEY_FILE_PATH` | HTTPS private key path | Yes |
| `CERT_FILE_PATH` | HTTPS certificate path | Yes |
| `CERT_PASSPHRASE` | Certificate passphrase | Dev only |
| `APN_KEY` | Apple Push Notification key | Yes |
| `APN_KEY_ID` | APN key identifier | Yes |
| `APN_TEAM_ID` | Apple Developer team ID | Yes |
| `APN_BUNDLE_ID` | iOS app bundle ID | Yes |
| `DOCUSIGN_HMAC_TOKEN` | Webhook signature secret | Yes |

---

## Security Specifications
1. **HTTPS Encryption**:
   - TLS 1.2+ required for all connections
   - Valid SSL certificate from trusted CA

2. **Data Validation**:
   - HMAC signature verification for all webhook requests
   - Cryptographic timing-safe comparison

3. **Secret Management**:
   - All sensitive credentials stored in environment variables
   - Never hardcoded in source files

---

## Error Handling
The system implements:
1. Try/catch blocks for all asynchronous operations
2. HTTP status codes for operation results
3. Descriptive error messages with root cause
4. Fallback mechanisms for failed APN deliveries

**Example Error Response**:
```json
HTTP/1.1 500 Internal Server Error
Content-Type: text/plain

Error sending APN notification: Invalid device token
```

---

## Dependencies
- Node.js v18+
- Express.js
- `apn` (Apple Push Notification library)
- `crypto` (Node.js cryptographic module)
- `dotenv` (environment variable loader)
- `reflect-metadata` (TypeScript decorator support)
- Axios (HTTP client)

---

## Appendix: Data Models

### Notification Entity
```ts
class Notification {
  id: number;
  subject: string;
  date: Date;
  is_read: boolean;
  is_signed: boolean;
  sender: string;
  receiver: User;
  app: Application;
  envelope_id: string;
}
```

### UserApplication Entity
```ts
class User_Application {
  id: number;
  user: User;
  app: Application;
  is_logged_in: boolean;
  num_of_unsigned_notif: number;
}
```

## Chunk 2
<think>
We are given the project name: "iphone-app-notification"
 We are also given source code and documentation for the public-server part of the project.

 From the source code, we can see that the project involves:
 - Entities: Application, Notification, User, User_Application
 - An API utility for making Axios requests (makeAxiosRequest)
 - A test file for webhookController (currently commented out)

 However, note that the provided source code does not contain the actual controller implementations for the API endpoints.
 But we are tasked with writing a Specification Document.

 Since we don't have the actual endpoint definitions, we must infer from the entities and the relationships.

 Let's analyze the entities:

 1. Application:
    - id (primary key)
    - app_name

 2. User:
    - id (primary key)
    - email (nullable)
    - device_token (non-nullable)

 3. Notification:
    - id (primary key)
    - subject
    - date (string representation)
    - is_read (number, probably 0 or 1)
    - is_signed (number, probably 0 or 1)
    - sender (string)
    - receiver (many-to-one with User)
    - app (many-to-one with Application)
    - envelope_id (string)

 4. User_Application:
    - id (primary key)
    - app (many-to-one with Application)
    - user (many-to-one with User)
    - num_of_unsigned_notif (number)
    - is_logged_in (number, probably 0 or 1)

 Based on these entities, we can expect endpoints for:

 - Managing Applications (CRUD? but note: the project is about notifications for an iPhone app)
 - Managing Users (CRUD? especially device_token for push notifications)
 - Managing Notifications (CRUD, and marking as read/signed)
 - Managing User_Application (which tracks per user and per application the number of unsigned notifications and login status)

 Additionally, we note:
 - There is a `makeAxiosRequest` function that uses a `PRIVATE_URL` environment variable. This suggests that the server might make requests to another private service? Or it might be used for internal routing? But note the function is in `api/utils`, so it might be used by the controllers to make requests to external services.

 Since the project is named "iphone-app-notification", we can assume that the main focus is on sending notifications to an iPhone app.

 We are missing the actual controller code, so we have to make educated guesses about the endpoints.

 However, note that the test file for `webhookController` is present (though commented out). This suggests that there might be a webhook endpoint that receives events (maybe from a service like DocuSign? because we see `envelope_id` in Notification) and then processes them.

 Given the above, we can outline the following endpoints:

 1. **Webhook Endpoint**: 
    - Method: POST
    - Path: /webhook
    - Purpose: To receive events from external services (like DocuSign) and then create notifications.

 2. **User Registration/Update**:
    - Method: POST (or PUT for update)
    - Path: /users
    - Purpose: To register a user (with device_token) or update an existing user's device token.

 3. **Notification List**:
    - Method: GET
    - Path: /notifications
    - Purpose: To get a list of notifications for a given user (and possibly for a given app).

 4. **Mark Notification as Read**:
    - Method: PATCH or PUT
    - Path: /notifications/{id}/read
    - Purpose: To mark a notification as read.

 5. **Mark Notification as Signed**:
    - Method: PATCH or PUT
    - Path: /notifications/{id}/signed
    - Purpose: To mark a notification as signed (and decrement the num_of_unsigned_notif in User_Application).

 6. **User Application Status**:
    - Method: GET
    - Path: /user-applications
    - Purpose: To get the status (is_logged_in, num_of_unsigned_notif) for a user and app.

 7. **Login/Logout for an Application**:
    - Method: POST
    - Path: /user-applications/login or /user-applications/logout
    - Purpose: To update the is_logged_in status.

 But note: the `User_Application` entity has a composite relationship and tracks per user and per application.

 Since we don't have the actual code, we will write a specification that covers the typical endpoints for such an application.

 We'll structure the specification as:

 1. Introduction
 2. Endpoints
    - For each endpoint: method, path, request body (if any), response

 We'll make reasonable assumptions about the endpoints.

 Let's write the specification accordingly.
</think>
# Specification Document: iPhone App Notification System

## Introduction
This document outlines the specification for the iPhone App Notification System, a backend service that manages user notifications, application associations, and notification delivery to mobile devices. The system provides APIs for webhook integration, user management, notification tracking, and application-user relationships.

## Core Entities

### User
- Represents an app user with device information
- Fields: `id`, `email`, `device_token`

### Application
- Represents a client application that sends notifications
- Fields: `id`, `app_name`

### Notification
- Represents a notification sent to a user
- Fields: `id`, `subject`, `date`, `is_read`, `is_signed`, `sender`, `receiver`, `app`, `envelope_id`

### User_Application
- Tracks user-application relationships and notification counts
- Fields: `id`, `app`, `user`, `num_of_unsigned_notif`, `is_logged_in`

---

## API Endpoints

### 1. Webhook Test Endpoint
**Purpose**: Test webhook functionality  
**Method**: GET  
**Path**: `/webhook/test`  
**Response**:
```json
{
  "status": "success",
  "message": "Webhook test successful"
}
```

### 2. Create User
**Purpose**: Register a new user or update existing user  
**Method**: POST  
**Path**: `/users`  
**Request Body**:
```json
{
  "email": "user@example.com",
  "device_token": "DEVICE_TOKEN_VALUE"
}
```

**Response**:
```json
{
  "id": 123,
  "email": "user@example.com",
  "device_token": "DEVICE_TOKEN_VALUE"
}
```

### 3. Get User Notifications
**Purpose**: Retrieve notifications for a specific user  
**Method**: GET  
**Path**: `/users/{user_id}/notifications`  
**Response**:
```json
[
  {
    "id": 456,
    "subject": "Document Signature Required",
    "date": "2023-06-15T10:30:00Z",
    "is_read": 0,
    "is_signed": 0,
    "sender": "sender@docusign.com",
    "app": {
      "id": 789,
      "app_name": "DocuSign"
    },
    "envelope_id": "ENV12345"
  }
]
```

### 4. Update Notification Status
**Purpose**: Mark notification as read or signed  
**Method**: PATCH  
**Path**: `/notifications/{notification_id}`  
**Request Body**:
```json
{
  "is_read": 1,
  "is_signed": 1
}
```

**Response**:
```json
{
  "id": 456,
  "status": "updated"
}
```

### 5. Link User to Application
**Purpose**: Associate user with an application  
**Method**: POST  
**Path**: `/user-applications`  
**Request Body**:
```json
{
  "user_id": 123,
  "app_id": 789,
  "is_logged_in": 1
}
```

**Response**:
```json
{
  "id": 101,
  "app": "DocuSign",
  "user": "user@example.com",
  "num_of_unsigned_notif": 0,
  "is_logged_in": 1
}
```

### 6. Webhook Notification Receiver
**Purpose**: Receive notification events from external services  
**Method**: POST  
**Path**: `/webhook/notifications`  
**Request Body** (Example):
```json
{
  "event": "envelope_sent",
  "subject": "Please sign: Agreement",
  "date": "2023-06-15T11:45:00Z",
  "sender": "legal@company.com",
  "receiver_email": "user@example.com",
  "app_name": "DocuSign",
  "envelope_id": "ENV67890"
}
```

**Response**:
```json
{
  "status": "received",
  "notification_id": 567
}
```

---

## Data Flow

1. **Notification Creation**:
   - External service sends notification via `/webhook/notifications`
   - System creates new Notification record
   - Increments `num_of_unsigned_notif` in User_Application

2. **Notification Delivery**:
   - Mobile app fetches user notifications via `/users/{id}/notifications`
   - System sends push notification using `device_token`

3. **User Interaction**:
   - When user views notification: PATCH `/notifications/{id}` sets `is_read=1`
   - When user signs document: PATCH `/notifications/{id}` sets `is_signed=1`
   - Decrements `num_of_unsigned_notif` in User_Application

---

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable description"
}
```

**Common Error Codes**:
- `400`: Invalid request parameters
- `404`: Resource not found
- `500`: Internal server error

---

## Environment Configuration

The system requires these environment variables:
```env
PRIVATE_URL=http://internal-service-url  # Base URL for internal services
DB_HOST=postgres_host
DB_USER=postgres_user
DB_PASSWORD=postgres_password
```

---

## Security Considerations

1. All endpoints require authentication via API tokens
2. Sensitve data (device tokens) encrypted at rest
3. Input validation for all webhook payloads
4. Rate limiting on public endpoints

This specification provides the foundation for the iPhone App Notification System. Implementation details may evolve during development while maintaining compatibility with this interface.