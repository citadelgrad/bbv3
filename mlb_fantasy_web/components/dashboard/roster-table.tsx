"use client"

import Link from "next/link"
import { Avatar } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import type { MockPlayer } from "@/lib/mock-data"
import { statusLabels } from "@/lib/mock-data"

interface RosterTableProps {
  players: MockPlayer[]
  className?: string
}

export function RosterTable({ players, className }: RosterTableProps) {
  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h3 className="font-semibold">Roster Pulse</h3>
        <Link href="/teams" className="text-sm text-primary hover:underline">
          View Full Roster
        </Link>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-xs text-muted-foreground">
              <th className="px-4 py-3 font-medium">Player</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Today&apos;s Outlook</th>
              <th className="px-4 py-3 font-medium text-right">7-Day Trend</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player) => (
              <tr
                key={player.id}
                className="border-b border-border last:border-0 hover:bg-muted/50 transition-colors"
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/player/${player.id}`}
                    className="flex items-center gap-3 hover:text-primary"
                  >
                    <Avatar alt={player.fullName} size="sm" />
                    <div>
                      <p className="font-medium">{player.fullName}</p>
                      <p className="text-xs text-muted-foreground">
                        {player.position} - {player.teamAbbrev}
                      </p>
                    </div>
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <Badge
                    variant={
                      player.status === "active"
                        ? "success"
                        : player.status === "dtd"
                          ? "warning"
                          : "destructive"
                    }
                    size="sm"
                  >
                    {statusLabels[player.status]}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Progress
                      value={player.outlook || 50}
                      className="w-24"
                      indicatorClassName={
                        (player.outlook || 50) >= 70
                          ? "bg-emerald-500"
                          : (player.outlook || 50) >= 40
                            ? "bg-yellow-500"
                            : "bg-red-500"
                      }
                    />
                    <span className="text-xs text-muted-foreground">{player.outlook || 50}%</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={cn(
                      "text-sm font-medium",
                      (player.trend || 0) > 0 && "text-emerald-400",
                      (player.trend || 0) < 0 && "text-red-400",
                      (player.trend || 0) === 0 && "text-muted-foreground"
                    )}
                  >
                    {(player.trend || 0) > 0 && "+"}
                    {player.trend || 0}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
