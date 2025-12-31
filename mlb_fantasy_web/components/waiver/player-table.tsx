"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import type { MockPlayer } from "@/lib/mock-data"
import { toast } from "sonner"

interface PlayerTableProps {
  players: MockPlayer[]
  className?: string
}

export function PlayerTable({ players, className }: PlayerTableProps) {
  const handleClaim = (player: MockPlayer) => {
    toast.success(`Waiver claim submitted for ${player.fullName}`)
  }

  const handleWatch = (player: MockPlayer) => {
    toast.success(`${player.fullName} added to watchlist`)
  }

  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h3 className="font-semibold">Available Players</h3>
        <span className="text-sm text-muted-foreground">
          Showing 1-{players.length} of 97 results
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-xs text-muted-foreground">
              <th className="px-4 py-3 font-medium">Rank</th>
              <th className="px-4 py-3 font-medium">Player</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Matchup Rating</th>
              <th className="px-4 py-3 font-medium text-right">AVG</th>
              <th className="px-4 py-3 font-medium text-right">HR</th>
              <th className="px-4 py-3 font-medium text-right">RBI</th>
              <th className="px-4 py-3 font-medium text-right">SB</th>
              <th className="px-4 py-3 font-medium text-right">OPS</th>
              <th className="px-4 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, index) => (
              <tr
                key={player.id}
                className="border-b border-border last:border-0 transition-colors hover:bg-muted/50"
              >
                <td className="px-4 py-3">
                  <div className="flex size-6 items-center justify-center rounded-full bg-primary/20 text-xs font-bold text-primary">
                    {index + 1}
                  </div>
                </td>
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
                    variant={index % 3 === 0 ? "success" : index % 3 === 1 ? "warning" : "outline"}
                    size="sm"
                  >
                    {index % 3 === 0 ? "Free Agent" : index % 3 === 1 ? "Waivers" : "Owned"}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Progress
                      value={player.outlook || 70}
                      className="w-20"
                      indicatorClassName={
                        (player.outlook || 70) >= 80
                          ? "bg-emerald-500"
                          : (player.outlook || 70) >= 60
                            ? "bg-yellow-500"
                            : "bg-red-500"
                      }
                    />
                  </div>
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats.avg > 0 ? player.stats.avg.toFixed(3) : "-"}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">{player.stats.hr || "-"}</td>
                <td className="px-4 py-3 text-right font-mono text-sm">{player.stats.rbi || "-"}</td>
                <td className="px-4 py-3 text-right font-mono text-sm">{player.stats.sb || "-"}</td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats.ops > 0 ? player.stats.ops.toFixed(3) : "-"}
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <Button size="sm" variant="default" onClick={() => handleClaim(player)}>
                      Claim
                    </Button>
                    <Button
                      size="icon-sm"
                      variant="outline"
                      onClick={() => handleWatch(player)}
                    >
                      <span className="material-symbols-outlined text-lg">visibility</span>
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Pagination */}
      <div className="flex items-center justify-between border-t border-border px-4 py-3">
        <Button variant="outline" size="sm" disabled>
          Previous
        </Button>
        <div className="flex gap-1">
          {[1, 2, 3, "...", 10].map((page, i) => (
            <button
              key={i}
              className={cn(
                "flex size-8 items-center justify-center rounded-md text-sm",
                page === 1
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted text-muted-foreground"
              )}
            >
              {page}
            </button>
          ))}
        </div>
        <Button variant="outline" size="sm">
          Next
        </Button>
      </div>
    </div>
  )
}
