"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FilterToolbar } from "@/components/waiver/filter-toolbar"
import { PlayerTable } from "@/components/waiver/player-table"
import { listPlayers } from "@/lib/api/players"
import type { Player } from "@/lib/api/types"
import type { Position } from "@/lib/mock-data"
import { toast } from "sonner"

const PAGE_SIZE = 20

export default function WaiverWirePage() {
  const [selectedPosition, setSelectedPosition] = React.useState<Position>("All")
  const [players, setPlayers] = React.useState<Player[]>([])
  const [total, setTotal] = React.useState(0)
  const [page, setPage] = React.useState(1)
  const [isLoading, setIsLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  // Fetch players when filters or page changes
  React.useEffect(() => {
    async function fetchPlayers() {
      setIsLoading(true)
      setError(null)

      try {
        const response = await listPlayers({
          limit: PAGE_SIZE,
          offset: (page - 1) * PAGE_SIZE,
          position: selectedPosition !== "All" ? selectedPosition : undefined,
          status: "active", // Only show active players on waiver wire
        })

        setPlayers(response.players)
        setTotal(response.total)
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to fetch players"
        setError(message)
        toast.error(message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchPlayers()
  }, [selectedPosition, page])

  // Reset to page 1 when filter changes
  const handlePositionChange = (position: Position) => {
    setSelectedPosition(position)
    setPage(1)
  }

  const handleRefresh = async () => {
    setIsLoading(true)
    try {
      const response = await listPlayers({
        limit: PAGE_SIZE,
        offset: (page - 1) * PAGE_SIZE,
        position: selectedPosition !== "All" ? selectedPosition : undefined,
        status: "active",
      })
      setPlayers(response.players)
      setTotal(response.total)
      toast.success("Player list refreshed")
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to refresh"
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex-1 space-y-6 p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Waiver Wire</h1>
          <Badge variant="default">{total} Players</Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
            <span className="material-symbols-outlined mr-2 text-lg">refresh</span>
            Refresh
          </Button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950 p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <Button variant="outline" size="sm" className="mt-2" onClick={handleRefresh}>
            Try Again
          </Button>
        </div>
      )}

      {/* Filter Toolbar */}
      <FilterToolbar
        selectedPosition={selectedPosition}
        onPositionChange={handlePositionChange}
      />

      {/* Player Table */}
      <PlayerTable
        players={players}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        isLoading={isLoading}
      />
    </div>
  )
}
