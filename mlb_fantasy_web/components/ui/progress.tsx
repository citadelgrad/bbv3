"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
  indicatorClassName?: string
  showLabel?: boolean
  size?: "sm" | "default" | "lg"
}

const sizeClasses = {
  sm: "h-1",
  default: "h-2",
  lg: "h-3",
}

function Progress({
  className,
  value = 0,
  max = 100,
  indicatorClassName,
  showLabel = false,
  size = "default",
  ...props
}: ProgressProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  return (
    <div className={cn("relative", className)} {...props}>
      <div
        className={cn(
          "w-full overflow-hidden rounded-full bg-secondary",
          sizeClasses[size]
        )}
      >
        <div
          className={cn(
            "h-full rounded-full bg-primary transition-all duration-300",
            indicatorClassName
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="absolute right-0 top-1/2 -translate-y-1/2 text-xs text-muted-foreground ml-2">
          {Math.round(percentage)}%
        </span>
      )}
    </div>
  )
}

export { Progress }
export type { ProgressProps }
