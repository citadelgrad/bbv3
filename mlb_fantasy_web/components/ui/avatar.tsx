"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string | null
  alt?: string
  fallback?: string
  size?: "sm" | "default" | "lg" | "xl"
}

const sizeClasses = {
  sm: "size-8 text-xs",
  default: "size-10 text-sm",
  lg: "size-12 text-base",
  xl: "size-16 text-lg",
}

function Avatar({
  className,
  src,
  alt = "",
  fallback,
  size = "default",
  ...props
}: AvatarProps) {
  const [hasError, setHasError] = React.useState(false)

  const initials = React.useMemo(() => {
    if (fallback) return fallback.slice(0, 2).toUpperCase()
    if (alt) {
      const words = alt.split(" ")
      if (words.length >= 2) {
        return (words[0][0] + words[words.length - 1][0]).toUpperCase()
      }
      return alt.slice(0, 2).toUpperCase()
    }
    return "?"
  }, [fallback, alt])

  return (
    <div
      className={cn(
        "relative flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-muted",
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {src && !hasError ? (
        <img
          src={src}
          alt={alt}
          className="aspect-square size-full object-cover"
          onError={() => setHasError(true)}
        />
      ) : (
        <span className="font-medium text-muted-foreground">{initials}</span>
      )}
    </div>
  )
}

export { Avatar }
export type { AvatarProps }
