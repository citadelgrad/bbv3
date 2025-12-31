"use client"

import { cn } from "@/lib/utils"

interface ToolRating {
  label: string
  value: number // 0-100
  abbreviation: string
}

interface ToolRatingsProps {
  ratings: ToolRating[]
  className?: string
}

export function ToolRatings({ ratings, className }: ToolRatingsProps) {
  // For simplicity, we'll render a bar chart instead of a radar chart
  // A proper radar chart would require a charting library like Recharts
  return (
    <div className={cn("rounded-xl border border-border bg-card p-4", className)}>
      <h3 className="mb-4 font-semibold">Tool Ratings</h3>
      <div className="space-y-3">
        {ratings.map((rating) => (
          <div key={rating.abbreviation} className="flex items-center gap-3">
            <span className="w-10 text-xs font-medium text-muted-foreground">
              {rating.abbreviation}
            </span>
            <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  rating.value >= 80
                    ? "bg-emerald-500"
                    : rating.value >= 60
                      ? "bg-primary"
                      : rating.value >= 40
                        ? "bg-yellow-500"
                        : "bg-red-500"
                )}
                style={{ width: `${rating.value}%` }}
              />
            </div>
            <span className="w-8 text-right text-sm font-medium">{rating.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
