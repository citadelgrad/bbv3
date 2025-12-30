import { createClient } from "@/lib/supabase/server";
import { ProfileForm } from "@/components/profile/profile-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default async function ProfilePage() {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  // Fetch profile from FastAPI backend
  const response = await fetch(`${API_URL}/api/v1/users/me`, {
    headers: {
      Authorization: `Bearer ${session?.access_token}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    return (
      <div className="max-w-2xl">
        <h1 className="text-3xl font-bold mb-8">Profile Settings</h1>
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Unable to load profile. Please try again later.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const profile = await response.json();

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Profile Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Your Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <ProfileForm initialData={profile} />
        </CardContent>
      </Card>
    </div>
  );
}
