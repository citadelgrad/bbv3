"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import type { Player } from "@/lib/api/types"
import { toast } from "sonner"

export interface WaiverPlayer extends Player {
  // Optional stats - may not be available from API yet
  stats?: {
    avg: number
    hr: number
    rbi: number
    sb: number
    ops: number
  }
  outlook?: number
}

interface PlayerTableProps {
  players: WaiverPlayer[]
  total?: number
  page?: number
  pageSize?: number
  onPageChange?: (page: number) => void
  isLoading?: boolean
  className?: string
}

export function PlayerTable({
  players,
  total = 0,
  page = 1,
  pageSize = 20,
  onPageChange,
  isLoading = false,
  className,
}: PlayerTableProps) {
  const handleClaim = (player: WaiverPlayer) => {
    toast.success(`Waiver claim submitted for ${player.full_name}`)
  }

  const handleWatch = (player: WaiverPlayer) => {
    toast.success(`${player.full_name} added to watchlist`)
  }

  const totalPages = Math.ceil(total / pageSize)
  const startIndex = (page - 1) * pageSize + 1
  const endIndex = Math.min(page * pageSize, total)

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else {
      if (page <= 3) {
        pages.push(1, 2, 3, "...", totalPages)
      } else if (page >= totalPages - 2) {
        pages.push(1, "...", totalPages - 2, totalPages - 1, totalPages)
      } else {
        pages.push(1, "...", page, "...", totalPages)
      }
    }
    return pages
  }

  if (isLoading) {
    return (
      <div className={cn("rounded-xl border border-border bg-card p-8", className)}>
        <div className="flex items-center justify-center gap-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          <p className="text-muted-foreground">Loading players...</p>
        </div>
      </div>
    )
  }

  if (players.length === 0) {
    return (
      <div className={cn("rounded-xl border border-border bg-card p-8", className)}>
        <div className="text-center">
          <span className="material-symbols-outlined text-4xl text-muted-foreground mb-2 block">
            person_search
          </span>
          <p className="text-muted-foreground">No players found</p>
        </div>
      </div>
    )
  }

  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h3 className="font-semibold">Available Players</h3>
        <span className="text-sm text-muted-foreground">
          Showing {startIndex}-{endIndex} of {total} results
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-xs text-muted-foreground">
              <th className="px-4 py-3 font-medium">Rank</th>
              <th className="px-4 py-3 font-medium">Player</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Position</th>
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
                    {startIndex + index}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/player/${player.id}`}
                    className="flex items-center gap-3 hover:text-primary"
                  >
                    <Avatar alt={player.full_name} size="sm" />
                    <div>
                      <p className="font-medium">{player.full_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {player.current_team_abbrev || player.current_team || "FA"}
                      </p>
                    </div>
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <Badge
                    variant={player.is_active ? "success" : "warning"}
                    size="sm"
                  >
                    {player.is_active ? "Active" : player.status}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <Badge variant="outline" size="sm">
                    {player.primary_position || "N/A"}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats?.avg ? player.stats.avg.toFixed(3) : "-"}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats?.hr ?? "-"}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats?.rbi ?? "-"}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats?.sb ?? "-"}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {player.stats?.ops ? player.stats.ops.toFixed(3) : "-"}
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
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-border px-4 py-3">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => onPageChange?.(page - 1)}
          >
            Previous
          </Button>
          <div className="flex gap-1">
            {getPageNumbers().map((pageNum, i) =>
              typeof pageNum === "number" ? (
                <button
                  key={i}
                  onClick={() => onPageChange?.(pageNum)}
                  className={cn(
                    "flex size-8 items-center justify-center rounded-md text-sm",
                    pageNum === page
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted text-muted-foreground"
                  )}
                >
                  {pageNum}
                </button>
              ) : (
                <span
                  key={i}
                  className="flex size-8 items-center justify-center text-sm text-muted-foreground"
                >
                  {pageNum}
                </span>
              )
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => onPageChange?.(page + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
