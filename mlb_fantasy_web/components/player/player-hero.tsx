import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import type { MockPlayer } from "@/lib/mock-data"
import { toast } from "sonner"

interface PlayerHeroProps {
  player: MockPlayer
  aiScore?: number
  grade?: string
  className?: string
}

const gradeColors: Record<string, string> = {
  "A+": "bg-emerald-500",
  A: "bg-emerald-500",
  "A-": "bg-emerald-400",
  "B+": "bg-blue-500",
  B: "bg-blue-500",
  "B-": "bg-blue-400",
  "C+": "bg-yellow-500",
  C: "bg-yellow-500",
  "C-": "bg-yellow-400",
  D: "bg-orange-500",
  F: "bg-red-500",
}

export function PlayerHero({ player, aiScore = 99, grade = "A+", className }: PlayerHeroProps) {
  const handleWatchlist = () => {
    toast.success(`${player.fullName} added to watchlist`)
  }

  const handleCompare = () => {
    toast.info("Player comparison coming soon")
  }

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-border bg-card",
        className
      )}
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-transparent" />

      <div className="relative flex flex-col gap-6 p-6 sm:flex-row sm:items-center">
        {/* Avatar */}
        <Avatar alt={player.fullName} size="xl" className="size-24 sm:size-32" />

        {/* Player Info */}
        <div className="flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold sm:text-3xl">{player.fullName}</h1>
            <span className="text-2xl text-muted-foreground">#{17}</span>
          </div>
          <p className="mb-3 text-lg text-muted-foreground">
            {player.position} | {player.team}
          </p>
          <div className="flex flex-wrap gap-2">
            <Badge variant="success">Waiver Wire</Badge>
            <Badge variant="default" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
              Yahoo Connected
            </Badge>
          </div>
        </div>

        {/* AI Score + Grade */}
        <div className="flex items-center gap-4 sm:flex-col sm:items-end">
          <div className="text-center">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">AI Scout</p>
            <p className="text-4xl font-bold text-primary">{aiScore}</p>
          </div>
          <div
            className={cn(
              "flex size-14 items-center justify-center rounded-lg text-2xl font-bold text-white",
              gradeColors[grade] || "bg-muted"
            )}
          >
            {grade}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 sm:flex-col">
          <Button variant="outline" onClick={handleWatchlist}>
            <span className="material-symbols-outlined mr-2 text-lg">bookmark_add</span>
            Add to Watchlist
          </Button>
          <Button variant="outline" onClick={handleCompare}>
            <span className="material-symbols-outlined mr-2 text-lg">compare</span>
            Compare Player
          </Button>
        </div>
      </div>
    </div>
  )
}
