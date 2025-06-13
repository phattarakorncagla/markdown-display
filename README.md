deepseek-r1-distill-llama-8b

# Project README: Document Signing Notification System

## Introduction
Welcome to the Document Signing Notification System project. This system is designed to handle notifications for document signing events via webhooks from DocuSign. It ensures timely updates through APNs for recipients.

## Project Requirements
- **Notifications**: Send real-time push notifications on document signing status.
- **Webhook Integration**: Handle DocuSign webhook events efficiently.
- **Database Management**: Store and update notification data using TypeORM.
- **Cross-Platform Support**: Ensure compatibility with both Android and iOS users via APNs.

## Dependencies
- **TypeORM**: ORM for database interactions (Already configured in code).
- **Express.js**: Web framework for setting up routes and controllers.
- **AxiOS**: Promise-based HTTP client for API requests.
- **Redis**: For quick access to APN keys.

## Getting Started
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-org/document-signing-notifications.git
   cd document-signing-notifications
   ```

2. **Set Up Environment Variables**:
   - Create a `.env` file with `PRIVATE_URL` pointing to your server URL.

3. **Install Dependencies**:
   ```bash
   npm install --save express axios typeorm redis
   ```
   Install all packages globally for simplicity.

4. **Database Setup**:
   ```bash
   npx typeorm init -f src/entity/
   ```
   Update `src/entity/schema.ts` if required.

5. **Run migrations**:
   ```bash
   npm run typeorm migration:run
   ```

6. **Start Application**:
   ```bash
   npm start
   ```
   Open `src/api/routes/routes.ts` to see the defined routes.

## How to Run the Application
1. Ensure Redis is running on port 6379.
2. Configure your DocuSign webhook endpoint URL in `src/controllers/webhookController.ts`.

## Relevant Code Examples

### 1. Notification Entity
```typescript
@Entity()
export class Notification {
  @PrimaryGeneratedColumn() id!: number;
  @Column() subject: string;
  @Column() date: string;
  @Column() is_read: number;
  @Column() is_signed: number;
  @Column() sender: string;
  
  @ManyToOne(() => User) receiver: User;
  @ManyToOne(() => Application) app: Application;
  @Column() envelope_id: string;

  constructor(
    subject: string,
    date: string,
    is_read: number,
    is_signed: number,
    sender: string,
    receiver: User,
    app: Application,
    envelope_id: string,
  ) { ... }
}
```

### 2. User Entity
```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn() id!: number;
  @Column({ type: 'text', nullable: true }) email: string | null;
  @Column() device_token: string;

  constructor(email?: string | null, device_token: string) { ... }
}
```

### 3. Webhook Controller
```typescript
webhookController.docusignNotification handles DocuSign events:
- For 'envelope-sent', it creates and sends APN notifications.
- For 'recipient-completed', it updates notification status.

## Conclusion
This project provides a robust solution for real-time document signing notifications using webhooks. It's designed to scale efficiently, handling both iOS and Android users via APNs. We encourage contributions and feedback to continuously improve the system. Happy coding!
