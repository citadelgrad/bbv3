"use client"

import { useParams } from "next/navigation"
import { useEffect, useState, useCallback } from "react"
import { PlayerHero } from "@/components/player/player-hero"
import { ScoutingCard } from "@/components/player/scouting-card"
import { ToolRatings } from "@/components/player/tool-ratings"
import { ProjectionsTable } from "@/components/player/projections-table"
import { Comparables } from "@/components/player/comparables"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { getPlayerById } from "@/lib/api/players"
import {
  getReportByPlayerName,
  researchPlayer,
  getJobStatus,
} from "@/lib/api/scouting"
import type { Player, ScoutingReport } from "@/lib/api/types"
import { mockPlayers } from "@/lib/mock-data"
import { toast } from "sonner"
import ReactMarkdown from "react-markdown"

type PageStatus = "loading" | "ready" | "not_found" | "error"
type ReportStatus = "loading" | "not_found" | "generating" | "ready" | "error"

export default function PlayerPage() {
  const params = useParams()
  const playerId = params.id as string

  // Player data state
  const [pageStatus, setPageStatus] = useState<PageStatus>("loading")
  const [player, setPlayer] = useState<Player | null>(null)
  const [pageError, setPageError] = useState<string | null>(null)

  // Scouting report state
  const [reportStatus, setReportStatus] = useState<ReportStatus>("loading")
  const [scoutingReport, setScoutingReport] = useState<ScoutingReport | null>(null)
  const [pollingMessage, setPollingMessage] = useState("")
  const [error, setError] = useState<string | null>(null)

  // Check if string is a valid UUID format
  const isValidUUID = (str: string) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    return uuidRegex.test(str)
  }

  // Convert mock player to Player type
  const mockToPlayer = (mock: typeof mockPlayers[0]): Player => ({
    id: mock.id,
    full_name: mock.fullName,
    first_name: mock.firstName,
    last_name: mock.lastName,
    name_suffix: null,
    name_normalized: mock.fullName.toLowerCase(),
    mlb_id: mock.mlbId,
    fangraphs_id: null,
    baseball_reference_id: null,
    yahoo_fantasy_id: null,
    espn_fantasy_id: null,
    birth_date: null,
    current_team: mock.team,
    current_team_abbrev: mock.teamAbbrev,
    primary_position: mock.position,
    bats: null,
    throws: null,
    status: mock.status,
    mlb_org: null,
    minor_league_level: null,
    is_active: mock.status === "active",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  })

  // Fetch player data on mount
  useEffect(() => {
    async function fetchPlayer() {
      setPageStatus("loading")
      setPageError(null)

      // If not a UUID, try to find in mock data (backward compatibility)
      if (!isValidUUID(playerId)) {
        const mockPlayer = mockPlayers.find((p) => p.id === playerId)
        if (mockPlayer) {
          setPlayer(mockToPlayer(mockPlayer))
          setPageStatus("ready")
          return
        }
        setPageStatus("not_found")
        setPageError(`Player not found`)
        return
      }

      // Fetch from API for UUID format
      try {
        const playerData = await getPlayerById(playerId)
        if (playerData) {
          setPlayer(playerData)
          setPageStatus("ready")
        } else {
          setPageStatus("not_found")
          setPageError(`Player not found`)
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to fetch player"
        setPageError(message)
        setPageStatus("error")
      }
    }

    fetchPlayer()
  }, [playerId])

  // Fetch scouting report when player is loaded
  useEffect(() => {
    if (!player) return

    const playerName = player.full_name

    async function fetchReport() {
      setReportStatus("loading")
      setError(null)

      try {
        const report = await getReportByPlayerName(playerName)
        if (report) {
          setScoutingReport(report)
          setReportStatus("ready")
        } else {
          setReportStatus("not_found")
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to fetch report"
        setError(message)
        setReportStatus("error")
      }
    }

    fetchReport()
  }, [player])

  // Handle report generation
  const handleGenerateReport = useCallback(async () => {
    if (!player) return

    setReportStatus("generating")
    setError(null)

    try {
      const response = await researchPlayer(player.full_name)

      if (response.status === "cached" || response.status === "generated") {
        setScoutingReport(response.report)
        setReportStatus("ready")
        toast.success(`Report ready for ${player.full_name}`)
      } else if (response.status === "pending") {
        setPollingMessage(`Researching ${player.full_name}...`)
        await pollForCompletion(response.job_id, player.full_name)
      } else if (response.status === "ambiguous") {
        const candidateNames = response.candidates
          .map((c) => `${c.full_name} (${c.current_team_abbrev || "N/A"})`)
          .join(", ")
        setError(
          `Multiple players found matching "${player.full_name}": ${candidateNames}. Please use the Scout page for more control.`
        )
        setReportStatus("error")
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to generate report"
      setError(message)
      setReportStatus("error")
      toast.error(message)
    }
  }, [player])

  // Poll for job completion
  async function pollForCompletion(jobId: string, playerName: string) {
    const maxAttempts = 60
    const intervalMs = 2000

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const jobStatus = await getJobStatus(jobId)

        if (jobStatus.status === "success" && jobStatus.result) {
          const reportData: ScoutingReport = {
            id: jobStatus.result.report_id,
            player_name: jobStatus.result.player_name,
            player_name_normalized: jobStatus.result.player_name.toLowerCase(),
            summary: jobStatus.result.summary,
            recent_stats: jobStatus.result.recent_stats,
            injury_status: jobStatus.result.injury_status,
            fantasy_outlook: jobStatus.result.fantasy_outlook,
            detailed_analysis: jobStatus.result.detailed_analysis,
            sources: jobStatus.result.sources,
            token_usage: jobStatus.result.token_usage,
            created_at: jobStatus.result.created_at,
            expires_at: jobStatus.result.expires_at,
          }
          setScoutingReport(reportData)
          setReportStatus("ready")
          toast.success(`Report generated for ${playerName}`)
          return
        }

        if (jobStatus.status === "failed" || jobStatus.status === "failure") {
          throw new Error(
            jobStatus.error_message || jobStatus.error || "Research job failed"
          )
        }

        setPollingMessage(
          `Researching ${playerName}... (${Math.floor((attempt * intervalMs) / 1000)}s)`
        )
        await new Promise((resolve) => setTimeout(resolve, intervalMs))
      } catch (err) {
        const message = err instanceof Error ? err.message : "Polling failed"
        setError(message)
        setReportStatus("error")
        toast.error(message)
        return
      }
    }

    setError("Research timed out. Please try again.")
    setReportStatus("error")
    toast.error("Research timed out")
  }

  // Loading state for entire page
  if (pageStatus === "loading") {
    return (
      <div className="flex-1 p-6 lg:p-8">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              <p className="text-muted-foreground">Loading player...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Player not found
  if (pageStatus === "not_found" || pageStatus === "error" || !player) {
    return (
      <div className="flex-1 p-6 lg:p-8">
        <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <span className="material-symbols-outlined text-4xl text-red-400 mb-4 block">
                error
              </span>
              <h3 className="text-lg font-semibold mb-2 text-red-600 dark:text-red-400">
                {pageStatus === "not_found" ? "Player Not Found" : "Error Loading Player"}
              </h3>
              <p className="text-muted-foreground mb-4">
                {pageError || "The requested player could not be found."}
              </p>
              <Button variant="outline" onClick={() => window.history.back()}>
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Transform player data for PlayerHero
  const playerHeroData = {
    id: player.id,
    fullName: player.full_name,
    team: player.current_team || "Unknown",
    position: player.primary_position || "Unknown",
  }

  const toolRatings = [
    { label: "Power", abbreviation: "PWR", value: 85 },
    { label: "Hit Tool", abbreviation: "AVG", value: 80 },
    { label: "Speed", abbreviation: "SPD", value: 75 },
    { label: "Defense", abbreviation: "DEF", value: 70 },
    { label: "Arm", abbreviation: "ARM", value: 75 },
    { label: "On-Base", abbreviation: "OBS", value: 80 },
  ]

  const projections = [
    { category: "AVG", value: ".285", confidence: "medium" as const },
    { category: "HR", value: "35", confidence: "medium" as const },
    { category: "RBI", value: "100", confidence: "medium" as const },
    { category: "SB", value: "15", confidence: "medium" as const },
    { category: "OPS", value: ".850", confidence: "medium" as const },
  ]

  const comparables = [
    { id: "comp-1", name: "Similar Player 1", team: "---", similarity: 85 },
    { id: "comp-2", name: "Similar Player 2", team: "---", similarity: 80 },
    { id: "comp-3", name: "Similar Player 3", team: "---", similarity: 75 },
  ]

  // Render scouting section
  const renderScoutingSection = () => {
    if (reportStatus === "loading") {
      return (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              <p className="text-muted-foreground">Loading scouting report...</p>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (reportStatus === "not_found") {
      return (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <span className="material-symbols-outlined text-4xl text-muted-foreground mb-4 block">
                search
              </span>
              <h3 className="text-lg font-semibold mb-2">No Scouting Report Available</h3>
              <p className="text-muted-foreground mb-6">
                Generate an AI-powered scouting report for {player.full_name}
              </p>
              <Button onClick={handleGenerateReport} size="lg">
                <span className="material-symbols-outlined mr-2">auto_awesome</span>
                Generate Scouting Report
              </Button>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (reportStatus === "generating") {
      return (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              <div>
                <p className="text-muted-foreground">{pollingMessage}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Deep research may take 30-60 seconds...
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (reportStatus === "error") {
      return (
        <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
          <CardContent className="pt-6">
            <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
            <Button onClick={handleGenerateReport} variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      )
    }

    if (scoutingReport) {
      return (
        <>
          <ScoutingCard title="AI Scouting Summary" variant="success">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{scoutingReport.summary}</ReactMarkdown>
            </div>
          </ScoutingCard>

          <div className="grid gap-6 lg:grid-cols-12">
            <div className="space-y-6 lg:col-span-4">
              <ScoutingCard title="Fantasy Outlook">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{scoutingReport.fantasy_outlook}</ReactMarkdown>
                </div>
              </ScoutingCard>
              <ScoutingCard title="Injury Status">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{scoutingReport.injury_status}</ReactMarkdown>
                </div>
              </ScoutingCard>
            </div>

            <div className="lg:col-span-8">
              <div className="rounded-xl border border-border bg-card p-4">
                <h3 className="mb-4 font-semibold">Deep Research & Analysis</h3>
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{scoutingReport.detailed_analysis}</ReactMarkdown>
                </div>
                <div className="mt-6">
                  <h4 className="mb-3 text-sm font-medium">Recent Stats</h4>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{scoutingReport.recent_stats}</ReactMarkdown>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {scoutingReport.sources && scoutingReport.sources.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="mb-3 font-semibold text-sm">Sources</h3>
                <div className="flex flex-wrap gap-2">
                  {scoutingReport.sources.map((source, idx) => (
                    <a
                      key={idx}
                      href={source.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-muted text-xs text-muted-foreground hover:text-foreground hover:bg-muted/80 transition-colors"
                    >
                      <span className="material-symbols-outlined text-sm">link</span>
                      {source.title}
                    </a>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Report generated: {new Date(scoutingReport.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )
    }

    return null
  }

  return (
    <div className="flex-1 space-y-6 p-6 lg:p-8">
      <PlayerHero player={playerHeroData} aiScore={75} grade="B+" />

      {renderScoutingSection()}

      <div className="grid gap-6 lg:grid-cols-2">
        <ToolRatings ratings={toolRatings} />
        <ProjectionsTable projections={projections} />
      </div>

      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="mb-4 font-semibold">Fantasy Points Trend (Last 10 Games)</h3>
        <div className="flex h-32 items-end justify-between gap-2">
          {[35, 42, 28, 55, 48, 62, 45, 38, 52, 58].map((value, i) => (
            <div
              key={i}
              className="flex-1 rounded-t bg-primary/80 transition-all hover:bg-primary"
              style={{ height: `${(value / 65) * 100}%` }}
            />
          ))}
        </div>
        <div className="mt-2 flex justify-between text-xs text-muted-foreground">
          <span>10 days ago</span>
          <span>Today</span>
        </div>
      </div>

      <Comparables comparables={comparables} />
    </div>
  )
}
