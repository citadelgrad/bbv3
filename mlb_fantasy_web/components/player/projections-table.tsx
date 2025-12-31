import { cn } from "@/lib/utils"

interface Projection {
  category: string
  value: string | number
  confidence?: "high" | "medium" | "low"
}

interface ProjectionsTableProps {
  projections: Projection[]
  timeframe?: "7D" | "ROS"
  className?: string
}

const confidenceColors = {
  high: "text-emerald-400",
  medium: "text-yellow-400",
  low: "text-red-400",
}

export function ProjectionsTable({
  projections,
  timeframe = "7D",
  className,
}: ProjectionsTableProps) {
  return (
    <div className={cn("rounded-xl border border-border bg-card", className)}>
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h3 className="font-semibold">Projections</h3>
        <div className="flex gap-1">
          <button
            className={cn(
              "rounded-md px-2 py-1 text-xs font-medium",
              timeframe === "7D"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted"
            )}
          >
            7D
          </button>
          <button
            className={cn(
              "rounded-md px-2 py-1 text-xs font-medium",
              timeframe === "ROS"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted"
            )}
          >
            ROS
          </button>
        </div>
      </div>
      <div className="p-2">
        <table className="w-full">
          <tbody>
            {projections.map((proj, i) => (
              <tr key={i} className="text-sm">
                <td className="px-2 py-2 text-muted-foreground">{proj.category}</td>
                <td className="px-2 py-2 text-right font-medium">{proj.value}</td>
                {proj.confidence && (
                  <td className={cn("px-2 py-2 text-right text-xs", confidenceColors[proj.confidence])}>
                    {proj.confidence}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
