"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { updateCurrentUser } from "@/lib/api/users";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import type { UserProfile } from "@/lib/api/types";

interface ProfileFormProps {
  initialData: UserProfile;
}

export function ProfileForm({ initialData }: ProfileFormProps) {
  const [username, setUsername] = useState(initialData.username);
  const [displayName, setDisplayName] = useState(
    initialData.display_name || ""
  );
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      await updateCurrentUser({
        username,
        display_name: displayName || null,
      });

      toast.success("Profile updated successfully");
      router.refresh();
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error("Failed to update profile");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <Input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          pattern="^[a-zA-Z0-9_]+$"
          minLength={3}
          maxLength={30}
          required
        />
        <p className="text-sm text-muted-foreground">
          3-30 characters, letters, numbers, and underscores only
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="displayName">Display Name</Label>
        <Input
          id="displayName"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          maxLength={100}
        />
        <p className="text-sm text-muted-foreground">
          Optional. How your name appears to others.
        </p>
      </div>

      <Button type="submit" disabled={loading}>
        {loading ? "Saving..." : "Save Changes"}
      </Button>
    </form>
  );
}
