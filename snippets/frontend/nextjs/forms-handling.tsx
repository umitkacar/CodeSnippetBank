/**
 * Next.js Forms Handling patterns
 */
'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { createPost } from './actions';

// Form with useFormState
export function FormWithState() {
  const [state, formAction] = useFormState(createPost, { message: '' });

  return (
    <form action={formAction}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      <SubmitButton />
      {state.message && <p>{state.message}</p>}
    </form>
  );
}

// Submit button with loading state
function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

// Progressive enhancement form
export function ProgressiveForm() {
  return (
    <form action="/api/contact" method="POST">
      <input type="text" name="name" required />
      <input type="email" name="email" required />
      <button type="submit">Send</button>
    </form>
  );
}

// File upload with server action
'use server';

export async function uploadFile(formData: FormData) {
  const file = formData.get('file') as File;

  if (!file) {
    return { error: 'No file uploaded' };
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  // Save file
  // await fs.writeFile(`./uploads/${file.name}`, buffer);

  return { success: true, filename: file.name };
}

// Multi-step form
'use client';

import { useState } from 'react';

export function MultiStepForm() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    address: '',
  });

  return (
    <form>
      {step === 1 && (
        <div>
          <input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <button type="button" onClick={() => setStep(2)}>
            Next
          </button>
        </div>
      )}
      {step === 2 && (
        <div>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <button type="button" onClick={() => setStep(3)}>
            Next
          </button>
        </div>
      )}
      {step === 3 && (
        <div>
          <input
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          />
          <button type="submit">Submit</button>
        </div>
      )}
    </form>
  );
}

// Form with React Hook Form
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormData = z.infer<typeof schema>;

export function RHFForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        Submit
      </button>
    </form>
  );
}
