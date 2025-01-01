'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Icons } from '@/components/ui/icons';

export default function VerifyEmailPage() {
  const [verifying, setVerifying] = useState(true);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      verifyEmail(token);
    } else {
      setVerifying(false);
    }
  }, [searchParams]);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const verifyEmail = async (token) => {
    try {
      const response = await fetch('/api/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Verification failed');
      }

      toast.success('Email verified successfully');
      router.push('/login');
    } catch (error) {
      toast.error(error.message);
      setVerifying(false);
    }
  };

  const resendVerification = async () => {
    try {
      setResending(true);
      const response = await fetch('/api/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: searchParams.get('email') }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to resend verification email');
      }

      toast.success('Verification email sent');
      setCountdown(60);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <Card className="w-[380px]">
        <CardHeader>
          <CardTitle>Email Verification</CardTitle>
          <CardDescription>
            {verifying
              ? 'Verifying your email address...'
              : 'Please verify your email address to continue'}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-4">
          {verifying ? (
            <Icons.spinner className="h-8 w-8 animate-spin" />
          ) : (
            <>
              <div className="rounded-full bg-yellow-100 p-3">
                <Icons.mail className="h-6 w-6 text-yellow-600" />
              </div>
              <p className="text-center text-sm text-muted-foreground">
                We&apos;ve sent you a verification email. Please check your inbox and click the verification link.
              </p>
            </>
          )}
        </CardContent>
        {!verifying && (
          <CardFooter className="flex flex-col space-y-4">
            <Button
              variant="outline"
              className="w-full"
              onClick={resendVerification}
              disabled={resending || countdown > 0}
            >
              {resending && <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />}
              {countdown > 0
                ? `Resend email in ${countdown}s`
                : 'Resend verification email'}
            </Button>
            <Button
              variant="ghost"
              className="w-full"
              onClick={() => router.push('/login')}
            >
              Back to login
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
} 