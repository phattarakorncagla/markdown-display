gemma-3-4b-document-writer
# Node.js Webhook API with Docusign Integration

This project demonstrates a Node.js backend that handles webhook events from Docusign. The API receives Docusign notifications, updates database records related to user applications and notifications, and sends push notifications using the device tokens of users. This comprehensive guide will walk you through the setup, dependencies, running the application, and understanding key components of this project.

## Project Requirements

- **Node.js:** Version 16 or higher
- **Express.js:** Framework for building web applications
- **Docusign Webhook API:** Understanding of how Docusign sends notifications via webhook events
- **TypeORM:** ORM for interacting with the database (PostgreSQL in this example)
- **Axios:** HTTP client for making API requests
- **Socket.IO:** Library for real-time communication

## Dependencies

Install necessary packages using npm or yarn:

```bash
npm install express typeorm axios cors dotenv socket.io --save
```

## Getting Started

### Setting up the Environment

1.  **Database Setup:** Ensure you have a PostgreSQL database running and create the necessary tables (Application, Notification, User, User_Application). TypeORM will handle the database migrations based on your entity definitions.

2.  **Environment Variables:** Create a `.env` file in the root directory to store environment variables:

```
PRIVATE_URL=http://localhost:3001 # Your backend URL
DOCIUSIGN_WEBHOOK_SECRET=your-secret-key # Docusign Webhook Secret
```

### Running the Application

1.  **Start the Backend:** Execute `npm start` or `yarn start`. This will start your Node.js server, typically running on port 3001 by default.

2.  **Configure Docusign Webhooks:** In your Docusign account settings, configure a webhook to point to your application's endpoint (`/webhooks/docusign`). Make sure the secret key matches the `DOCIUSIGN_WEBHOOK_SECRET` in your `.env` file.

## How to Run the Application

1.  **Start the Server:** Navigate to the project directory in your terminal and run `npm start`. This will start the Node.js server.

2.  **Docusign Webhook Trigger:** When a Docusign event occurs (e.g., document signed, envelope completed), Docusign sends an HTTP POST request to your application's webhook endpoint (`/webhooks/docusign`).

3.  **Webhook Handling:** The `/webhooks/docusign` route in the `webhookController.ts` file handles incoming requests from Docusign. It parses the JSON payload, extracts relevant data (like recipient, subject, and envelope ID), and performs the necessary actions:

    -   It updates a notification in the database with the received information.
    -   It updates the user's application record to reflect the new notification status.
    -   It sends a push notification to the user using their device token (using Socket.IO).

## Relevant Code Examples

### `src/api/routes/webhookRoutes.ts`

This file defines the endpoint for handling Docusign webhooks:

```typescript
import express, { Router } from 'express';
import webhookController from '../controllers/webhookController';

const router: Router = express.Router();

router.post('/docusign', webhookController.docusignNotification);

export default router;
```

### `src/api/controllers/webhookController.ts`

This file contains the logic for handling Docusign notifications:

```typescript
import { Request, Response } from 'express';
import { makeAxiosRequest } from '../utils/axiosRequest';
import { Notification } from '../../entity/Notification';
import { User } from '../../entity/User';
import { Application } from '../../entity/Application';
import { User_Application } from '../../entity/User_Application';

export const docusignNotification = async (req: Request, res: Response) => {
  const notificationResponse = req.body;

  try {
    const notificationData: Notification = {
      subject: notificationResponse.data.subject,
      date: notificationResponse.data.date,
      is_read: notificationResponse.data.is_read,
      is_signed: notificationResponse.data.is_signed,
      sender: notificationResponse.data.sender,
      receiver: new User(notificationResponse.data.receiver.email, notificationResponse.data.receiver.device_token),
      app: new Application(notificationResponse.data.app.name),
      envelope_id: notificationResponse.data.envelope_id,
    };

    const updatedNotification = await makeAxiosRequest(
      `notifications/update/${notificationData.id}`,
      'put',
      notificationData,
    );
    notificationData = updatedNotification.data;

    const userApplication = await makeAxiosRequest(
      `userApplications/update/${req.user.app.id}`,
      'put',
      {
        num_of_unsigned_notif: req.user.numOfUnsignedNotif - 1,
        is_logged_in: 1, // Assuming login triggers this
      },
    );

  } catch (error) {
    console.error('Error processing JSON from webhook:', error);
    res
      .status(500)
      .send(`Error processing JSON from webhook: ${(error as Error).message}`);
  }

  res.status(200).send('Success');
};
```

### `src/api/utils/axiosRequest.ts`

This file handles making HTTP requests using Axios:

```typescript
import axios, { AxiosResponse } from 'axios';

export async function makeAxiosRequest<T>(
  url: string,
  method: 'get' | 'post' | 'put',
  data?: object,
): Promise<AxiosResponse<T>> {
  const PRIVATE_URL = process.env.PRIVATE_URL || 'http://localhost';

  try {
    const response = await axios({
      url: `${PRIVATE_URL}/${url}`,
      method,
      data,
    });
    return response;
  } catch (error) {
    console.error('Error in axios request:', error);
    throw error;
  }
}
```

### `src/entity/Notification.ts` and `src/entity/User.ts`, `src/entity/Application.ts` and `src/entity/User_Application.ts`

These files define the database entities used in this application: Notification, User, Application, and User\_Application.

## Conclusion

This project demonstrates a robust backend for handling Docusign webhooks, updating database records, and sending push notifications to users. By following these steps and understanding the key components of the code, you can build your own webhook integration solution for managing digital signatures and user engagement.  Further development could include more complex notification logic, event-driven architecture, and improved error handling.
