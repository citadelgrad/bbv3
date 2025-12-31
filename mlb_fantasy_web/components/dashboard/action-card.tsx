import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface ActionCardProps {
  title: string
  subtitle?: string
  badge?: string
  badgeVariant?: "default" | "success" | "warning" | "destructive"
  playerName?: string
  playerTeam?: string
  playerImage?: string
  actionLabel: string
  actionHref?: string
  onAction?: () => void
  icon?: string
  className?: string
}

export function ActionCard({
  title,
  subtitle,
  badge,
  badgeVariant = "default",
  playerName,
  playerTeam,
  playerImage,
  actionLabel,
  actionHref,
  onAction,
  icon,
  className,
}: ActionCardProps) {
  const ActionButton = actionHref ? (
    <Button size="sm" variant="outline" asChild>
      <Link href={actionHref}>{actionLabel}</Link>
    </Button>
  ) : (
    <Button size="sm" variant="outline" onClick={onAction}>
      {actionLabel}
    </Button>
  )

  return (
    <div
      className={cn(
        "flex flex-col gap-4 rounded-xl border border-border bg-card p-4",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            {icon && (
              <span className="material-symbols-outlined text-lg text-primary">{icon}</span>
            )}
            <span className="text-sm font-medium text-muted-foreground">{title}</span>
          </div>
          {subtitle && <span className="text-xs text-muted-foreground">{subtitle}</span>}
        </div>
        {badge && <Badge variant={badgeVariant}>{badge}</Badge>}
      </div>

      {playerName && (
        <div className="flex items-center gap-3">
          <Avatar src={playerImage} alt={playerName} size="lg" />
          <div className="flex-1">
            <p className="font-semibold">{playerName}</p>
            {playerTeam && <p className="text-sm text-muted-foreground">{playerTeam}</p>}
          </div>
        </div>
      )}

      <div className="flex justify-end">{ActionButton}</div>
    </div>
  )
}
