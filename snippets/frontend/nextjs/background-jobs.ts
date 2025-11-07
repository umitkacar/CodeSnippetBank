/**
 * Next.js Background Jobs and Queue Processing
 */

// Bullmq queue setup
import { Queue, Worker } from 'bullmq';
import { Redis } from 'ioredis';

const connection = new Redis(process.env.REDIS_URL || '');

export const emailQueue = new Queue('emails', { connection });

// Add job to queue
export async function queueEmail(to: string, subject: string, body: string) {
  await emailQueue.add('send-email', {
    to,
    subject,
    body,
  });
}

// Process jobs
export const emailWorker = new Worker(
  'emails',
  async (job) => {
    const { to, subject, body } = job.data;
    // Send email logic
    console.log(`Sending email to ${to}`);
  },
  { connection }
);

// Scheduled jobs with node-cron
import cron from 'node-cron';

// Run every day at midnight
export const dailyCleanupJob = cron.schedule('0 0 * * *', async () => {
  console.log('Running daily cleanup...');
  // Cleanup logic
});

// API route for background processing
export async function POST(request: Request) {
  const data = await request.json();

  // Queue for background processing
  await emailQueue.add('process-data', data);

  return Response.json({ queued: true });
}
