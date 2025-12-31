"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { positions, type Position } from "@/lib/mock-data"

interface FilterToolbarProps {
  selectedPosition: Position
  onPositionChange: (position: Position) => void
  className?: string
}

export function FilterToolbar({
  selectedPosition,
  onPositionChange,
  className,
}: FilterToolbarProps) {
  return (
    <div
      className={cn(
        "sticky top-0 z-10 flex flex-wrap items-center gap-4 rounded-xl border border-border bg-card/95 p-4 backdrop-blur",
        className
      )}
    >
      {/* Position Chips */}
      <div className="flex flex-wrap gap-2">
        {positions.map((pos) => (
          <button
            key={pos}
            onClick={() => onPositionChange(pos)}
            className={cn(
              "rounded-full px-3 py-1 text-sm font-medium transition-colors",
              selectedPosition === pos
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            {pos}
          </button>
        ))}
      </div>

      {/* Divider */}
      <div className="h-6 w-px bg-border" />

      {/* Advanced Filters */}
      <div className="flex items-center gap-3 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground">Min AVG:</span>
          <input
            type="text"
            defaultValue=".265"
            className="w-16 rounded-md border border-input bg-background px-2 py-1 text-sm"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground">Max ERA:</span>
          <input
            type="text"
            defaultValue="3.50"
            className="w-16 rounded-md border border-input bg-background px-2 py-1 text-sm"
          />
        </div>
      </div>

      <Button variant="outline" size="sm" className="ml-auto">
        <span className="material-symbols-outlined mr-1 text-lg">tune</span>
        More Filters
      </Button>
    </div>
  )
}
