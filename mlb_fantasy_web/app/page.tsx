import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center space-y-8 max-w-2xl">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          MLB Fantasy Baseball
        </h1>
        <p className="text-xl text-muted-foreground">
          Build your dream team and compete with friends in the ultimate fantasy
          baseball experience.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/login">Sign In</Link>
          </Button>
          <Button variant="outline" size="lg" asChild>
            <Link href="/signup">Create Account</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
