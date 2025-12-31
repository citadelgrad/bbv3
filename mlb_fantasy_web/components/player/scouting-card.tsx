import { cn } from "@/lib/utils"

interface ScoutingCardProps {
  title: string
  variant?: "default" | "success" | "warning"
  children: React.ReactNode
  className?: string
}

const variantStyles = {
  default: "border-border bg-card",
  success: "border-emerald-500/30 bg-emerald-500/10",
  warning: "border-yellow-500/30 bg-yellow-500/10",
}

export function ScoutingCard({
  title,
  variant = "default",
  children,
  className,
}: ScoutingCardProps) {
  return (
    <div className={cn("rounded-xl border p-4", variantStyles[variant], className)}>
      <h3 className="mb-3 font-semibold">{title}</h3>
      <div className="text-sm text-muted-foreground">{children}</div>
    </div>
  )
}
