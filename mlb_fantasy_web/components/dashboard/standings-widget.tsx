import { cn } from "@/lib/utils"
import type { MockLeagueStanding } from "@/lib/mock-data"

interface StandingsWidgetProps {
  standings: MockLeagueStanding[]
  className?: string
}

export function StandingsWidget({ standings, className }: StandingsWidgetProps) {
  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-semibold">League Standings</h3>
      </div>
      <div className="p-2">
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs text-muted-foreground">
              <th className="px-2 py-2 font-medium">#</th>
              <th className="px-2 py-2 font-medium">Team</th>
              <th className="px-2 py-2 font-medium text-right">Pts</th>
            </tr>
          </thead>
          <tbody>
            {standings.slice(0, 5).map((team) => (
              <tr
                key={team.rank}
                className={cn(
                  "text-sm",
                  team.isUser && "bg-primary/10 rounded"
                )}
              >
                <td className="px-2 py-2 font-medium">{team.rank}</td>
                <td className="px-2 py-2">
                  <div className="flex flex-col">
                    <span className={cn("font-medium", team.isUser && "text-primary")}>
                      {team.teamName}
                    </span>
                    <span className="text-xs text-muted-foreground">{team.record}</span>
                  </div>
                </td>
                <td className="px-2 py-2 text-right font-medium">{team.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
