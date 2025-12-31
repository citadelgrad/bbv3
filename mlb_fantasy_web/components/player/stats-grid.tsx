import { cn } from "@/lib/utils"

interface StatItem {
  label: string
  value: string | number
  trend?: number
  suffix?: string
}

interface StatsGridProps {
  stats: StatItem[]
  columns?: 2 | 3 | 4
  className?: string
}

export function StatsGrid({ stats, columns = 4, className }: StatsGridProps) {
  const gridCols = {
    2: "grid-cols-2",
    3: "grid-cols-3",
    4: "grid-cols-2 sm:grid-cols-4",
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {stats.map((stat, i) => (
        <div
          key={i}
          className="rounded-lg border border-border bg-card p-4 text-center"
        >
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            {stat.label}
          </p>
          <p className="text-2xl font-bold">
            {stat.value}
            {stat.suffix && <span className="text-lg text-muted-foreground">{stat.suffix}</span>}
          </p>
          {stat.trend !== undefined && (
            <p
              className={cn(
                "text-xs font-medium mt-1",
                stat.trend > 0 && "text-emerald-400",
                stat.trend < 0 && "text-red-400",
                stat.trend === 0 && "text-muted-foreground"
              )}
            >
              {stat.trend > 0 && "+"}
              {stat.trend}%
            </p>
          )}
        </div>
      ))}
    </div>
  )
}
