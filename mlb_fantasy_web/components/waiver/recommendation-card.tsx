import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import type { MockRecommendation } from "@/lib/mock-data"

interface RecommendationCardProps {
  recommendation: MockRecommendation
  className?: string
}

export function RecommendationCard({ recommendation, className }: RecommendationCardProps) {
  const { player, matchScore, reason, projections } = recommendation

  return (
    <div
      className={cn(
        "flex flex-col gap-4 rounded-xl border border-border bg-card p-4 transition-all hover:border-primary/50",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Avatar alt={player.fullName} size="lg" />
          <div>
            <p className="font-semibold">{player.fullName}</p>
            <p className="text-sm text-muted-foreground">
              {player.position}, {player.teamAbbrev}
            </p>
          </div>
        </div>
        <Badge variant="success" size="lg">
          {matchScore}% Match
        </Badge>
      </div>

      {/* Reason */}
      <p className="text-sm text-muted-foreground">{reason}</p>

      {/* Projections */}
      <div className="flex flex-wrap gap-3">
        {projections.hr !== undefined && (
          <div className="rounded-md bg-muted px-2 py-1">
            <span className="text-xs text-muted-foreground">Proj. HR: </span>
            <span className="text-sm font-medium">{projections.hr}</span>
          </div>
        )}
        {projections.sb !== undefined && (
          <div className="rounded-md bg-muted px-2 py-1">
            <span className="text-xs text-muted-foreground">SB Pot: </span>
            <span className="text-sm font-medium">High</span>
          </div>
        )}
        {projections.k9 !== undefined && (
          <div className="rounded-md bg-muted px-2 py-1">
            <span className="text-xs text-muted-foreground">K/9: </span>
            <span className="text-sm font-medium">{projections.k9}</span>
          </div>
        )}
        {projections.era !== undefined && (
          <div className="rounded-md bg-muted px-2 py-1">
            <span className="text-xs text-muted-foreground">ERA (L14): </span>
            <span className="text-sm font-medium">{projections.era.toFixed(2)}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button size="sm" className="flex-1" asChild>
          <Link href={`/player/${player.id}`}>View Analysis</Link>
        </Button>
        <Button size="sm" variant="outline">
          <span className="material-symbols-outlined text-lg">bookmark_add</span>
        </Button>
      </div>
    </div>
  )
}
