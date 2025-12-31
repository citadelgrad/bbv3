"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RecommendationCard } from "@/components/waiver/recommendation-card"
import { FilterToolbar } from "@/components/waiver/filter-toolbar"
import { PlayerTable } from "@/components/waiver/player-table"
import { mockPlayers, mockRecommendations, type Position } from "@/lib/mock-data"

export default function WaiverWirePage() {
  const [selectedPosition, setSelectedPosition] = React.useState<Position>("All")

  const filteredPlayers = React.useMemo(() => {
    if (selectedPosition === "All") return mockPlayers
    return mockPlayers.filter((p) => p.position === selectedPosition)
  }, [selectedPosition])

  return (
    <div className="flex-1 space-y-6 p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Waiver Wire</h1>
          <Badge variant="default">Week 12</Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <span className="material-symbols-outlined mr-2 text-lg">tune</span>
            Configure AI Model
          </Button>
          <Button variant="outline" size="sm">
            <span className="material-symbols-outlined mr-2 text-lg">refresh</span>
            Refresh Availability
          </Button>
        </div>
      </div>

      {/* AI Top Targets */}
      <div>
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="flex items-center gap-2 font-semibold">
              <span className="material-symbols-outlined text-primary">auto_awesome</span>
              AI Top Targets
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Our predictive algorithms found these players for your 5x5 Roto league
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="material-symbols-outlined text-xs text-muted-foreground">
              trending_up
            </span>
            <span className="text-muted-foreground">League Trend:</span>
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className={`h-4 w-1 rounded-full ${i <= 4 ? "bg-primary" : "bg-muted"}`}
                />
              ))}
            </div>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {mockRecommendations.map((rec, i) => (
            <RecommendationCard key={i} recommendation={rec} />
          ))}
        </div>
      </div>

      {/* Filter Toolbar */}
      <FilterToolbar
        selectedPosition={selectedPosition}
        onPositionChange={setSelectedPosition}
      />

      {/* Player Table */}
      <PlayerTable players={filteredPlayers} />
    </div>
  )
}
