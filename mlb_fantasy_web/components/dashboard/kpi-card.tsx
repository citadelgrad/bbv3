import { cn } from "@/lib/utils"

interface KpiCardProps {
  title: string
  value: string
  trend?: number | string
  trendLabel?: string
  icon?: string
  className?: string
}

export function KpiCard({ title, value, trend, trendLabel, icon, className }: KpiCardProps) {
  const trendIsPositive = typeof trend === "number" ? trend > 0 : trend?.startsWith("+")
  const trendIsNegative = typeof trend === "number" ? trend < 0 : trend?.startsWith("-")

  return (
    <div
      className={cn(
        "flex flex-col gap-2 rounded-xl border border-border bg-card p-6",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">{title}</span>
        {icon && (
          <span className="material-symbols-outlined text-xl text-muted-foreground">{icon}</span>
        )}
      </div>
      <div className="flex items-end gap-3">
        <span className="text-3xl font-bold">{value}</span>
        {(trend !== undefined || trendLabel) && (
          <span
            className={cn(
              "mb-1 text-sm font-medium",
              trendIsPositive && "text-emerald-400",
              trendIsNegative && "text-red-400",
              !trendIsPositive && !trendIsNegative && "text-muted-foreground"
            )}
          >
            {typeof trend === "number" && trend > 0 && "+"}
            {trend}
            {typeof trend === "number" && "%"}
            {trendLabel && ` ${trendLabel}`}
          </span>
        )}
      </div>
    </div>
  )
}
