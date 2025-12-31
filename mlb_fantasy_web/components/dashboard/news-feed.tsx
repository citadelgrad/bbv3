import { cn } from "@/lib/utils"
import type { MockNewsItem } from "@/lib/mock-data"

interface NewsFeedProps {
  news: MockNewsItem[]
  className?: string
}

const typeColors: Record<MockNewsItem["type"], string> = {
  injury: "bg-red-500",
  transaction: "bg-primary",
  performance: "bg-emerald-500",
}

export function NewsFeed({ news, className }: NewsFeedProps) {
  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-semibold">Player News</h3>
      </div>
      <div className="divide-y divide-border">
        {news.map((item) => (
          <div key={item.id} className="flex gap-3 px-4 py-3">
            <div className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", typeColors[item.type])} />
            <div className="flex-1 min-w-0">
              <p className="text-sm">
                <span className="font-medium">{item.playerName}</span>
                <span className="text-muted-foreground"> - {item.headline}</span>
              </p>
              <p className="text-xs text-muted-foreground">{item.timestamp}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
