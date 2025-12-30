import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.email}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>My Teams</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No teams yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Join or create a league to get started
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>My Leagues</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No leagues yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Coming soon: Create or join a league
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No recent activity</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
