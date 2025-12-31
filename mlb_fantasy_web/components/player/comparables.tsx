import Link from "next/link"
import { Avatar } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

interface Comparable {
  id: string
  name: string
  team: string
  similarity: number
  imageUrl?: string
}

interface ComparablesProps {
  comparables: Comparable[]
  className?: string
}

export function Comparables({ comparables, className }: ComparablesProps) {
  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-semibold">Similar Players</h3>
      </div>
      <div className="divide-y divide-border">
        {comparables.map((comp) => (
          <Link
            key={comp.id}
            href={`/player/${comp.id}`}
            className="flex items-center gap-3 px-4 py-3 hover:bg-muted/50 transition-colors"
          >
            <Avatar alt={comp.name} size="sm" />
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{comp.name}</p>
              <p className="text-xs text-muted-foreground">{comp.team}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-primary">{comp.similarity}%</p>
              <Progress
                value={comp.similarity}
                className="w-16 h-1"
                indicatorClassName="bg-primary"
              />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
