/**
 * Next.js Email Templates with React Email
 */
import { Html, Head, Body, Container, Text, Link, Button } from '@react-email/components';

export function WelcomeEmail({ name }: { name: string }) {
  return (
    <Html>
      <Head />
      <Body style={{ fontFamily: 'Arial, sans-serif' }}>
        <Container>
          <Text>Welcome, {name}!</Text>
          <Button href="https://example.com">Get Started</Button>
        </Container>
      </Body>
    </Html>
  );
}

export function ResetPasswordEmail({ resetLink }: { resetLink: string }) {
  return (
    <Html>
      <Head />
      <Body>
        <Container>
          <Text>Reset Your Password</Text>
          <Text>Click the link below to reset your password:</Text>
          <Link href={resetLink}>Reset Password</Link>
        </Container>
      </Body>
    </Html>
  );
}
