import { cn } from "@/lib/utils"

interface MatchupWidgetProps {
  userScore: number
  opponentScore: number
  opponentName: string
  winProbability: number
  className?: string
}

export function MatchupWidget({
  userScore,
  opponentScore,
  opponentName,
  winProbability,
  className,
}: MatchupWidgetProps) {
  const isWinning = userScore > opponentScore

  return (
    <div className={cn("rounded-xl border border-border bg-card p-4", className)}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold">Weekly Matchup</h3>
        <span className="text-xs text-muted-foreground">Week 12</span>
      </div>

      <div className="mb-4 flex items-center justify-between">
        <div className="text-center">
          <p className="text-xs text-muted-foreground">You</p>
          <p className={cn("text-2xl font-bold", isWinning && "text-emerald-400")}>{userScore}</p>
        </div>
        <div className="text-center">
          <p className="text-lg font-medium text-muted-foreground">vs</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground">{opponentName}</p>
          <p className={cn("text-2xl font-bold", !isWinning && "text-red-400")}>{opponentScore}</p>
        </div>
      </div>

      {/* Win Probability Gauge */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Win Probability</span>
          <span className="font-medium text-emerald-400">{winProbability}%</span>
        </div>
        <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-400"
            style={{ width: `${winProbability}%` }}
          />
          <div
            className="absolute right-0 top-0 h-full rounded-full bg-gradient-to-l from-red-500 to-red-400"
            style={{ width: `${100 - winProbability}%` }}
          />
        </div>
      </div>
    </div>
  )
}
