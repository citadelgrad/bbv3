"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface TeamSelectorProps {
  teams: { id: string; name: string }[]
  selectedTeamId?: string
  onSelect?: (teamId: string) => void
  className?: string
}

export function TeamSelector({ teams, selectedTeamId, onSelect, className }: TeamSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const selectedTeam = teams.find((t) => t.id === selectedTeamId) || teams[0]

  return (
    <div className={cn("relative", className)}>
      <Button
        variant="outline"
        className="w-full justify-between gap-2"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="truncate">{selectedTeam?.name || "Select Team"}</span>
        <span className="material-symbols-outlined text-lg">
          {isOpen ? "expand_less" : "expand_more"}
        </span>
      </Button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 rounded-lg border border-border bg-popover shadow-lg">
          {teams.map((team) => (
            <button
              key={team.id}
              className={cn(
                "w-full px-4 py-2 text-left text-sm hover:bg-muted transition-colors first:rounded-t-lg last:rounded-b-lg",
                team.id === selectedTeamId && "bg-primary/10 text-primary"
              )}
              onClick={() => {
                onSelect?.(team.id)
                setIsOpen(false)
              }}
            >
              {team.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
