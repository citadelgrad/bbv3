import { LoginForm } from "@/components/auth/login-form";
import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="text-muted-foreground">Sign in to your account</p>
        </div>

        <LoginForm />

        <div className="space-y-2 text-center text-sm">
          <p>
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="underline hover:text-primary">
              Sign up
            </Link>
          </p>
          <p>
            <Link
              href="/forgot-password"
              className="underline hover:text-primary"
            >
              Forgot your password?
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
