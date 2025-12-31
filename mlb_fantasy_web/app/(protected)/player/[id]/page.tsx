"use client"

import { useParams } from "next/navigation"
import { PlayerHero } from "@/components/player/player-hero"
import { ScoutingCard } from "@/components/player/scouting-card"
import { StatsGrid } from "@/components/player/stats-grid"
import { ToolRatings } from "@/components/player/tool-ratings"
import { ProjectionsTable } from "@/components/player/projections-table"
import { Comparables } from "@/components/player/comparables"
import { mockPlayers } from "@/lib/mock-data"

export default function PlayerPage() {
  const params = useParams()
  const playerId = params.id as string

  // Find player from mock data, or use first player as fallback
  const player = mockPlayers.find((p) => p.id === playerId) || mockPlayers[0]

  // Mock scouting report data
  const scoutingReport = {
    recentPerformance:
      "Ohtani continues to be the most dominant two-way player in baseball. His recent 5-game hitting streak includes 3 home runs and 8 RBIs. His plate discipline remains elite with a 12% walk rate.",
    fantasyVerdict:
      "MUST START - Ohtani is a league-winner in any format. His combination of power, speed, and pitching makes him the most valuable fantasy asset available.",
    injuryStatus: "Healthy - No injury concerns. Full workload expected for the remainder of the season.",
    deepResearch: [
      "Ohtani's hard hit rate of 52.3% ranks in the 98th percentile among all MLB hitters. His expected slugging percentage (.612) suggests his power output is sustainable.",
      "His stolen base success rate of 87% shows excellent base-running instincts. With 59 steals this season, he's a true 40-40 candidate.",
      "Pitching metrics remain elite: 11.4 K/9, 2.8 BB/9, and a 0.95 WHIP. His splitter continues to generate swings and misses at a 42% rate.",
    ],
  }

  const seasonStats = [
    { label: "AVG", value: ".304", trend: 2.1 },
    { label: "HR", value: "54", trend: 8.5 },
    { label: "OPS", value: "1.036", trend: 3.2 },
    { label: "SB", value: "59", trend: 15.0 },
  ]

  const recentStats = [
    { label: "AVG", value: ".342" },
    { label: "Hard Hit %", value: "52.3%" },
    { label: "xSLG", value: ".612" },
    { label: "Proj. HR", value: "58" },
  ]

  const toolRatings = [
    { label: "Power", abbreviation: "PWR", value: 95 },
    { label: "Hit Tool", abbreviation: "AVG", value: 85 },
    { label: "Speed", abbreviation: "SPD", value: 80 },
    { label: "Defense", abbreviation: "DEF", value: 60 },
    { label: "Arm", abbreviation: "ARM", value: 90 },
    { label: "On-Base", abbreviation: "OBS", value: 88 },
  ]

  const projections = [
    { category: "AVG", value: ".298", confidence: "high" as const },
    { category: "HR", value: "58", confidence: "high" as const },
    { category: "RBI", value: "135", confidence: "medium" as const },
    { category: "SB", value: "62", confidence: "high" as const },
    { category: "OPS", value: "1.025", confidence: "high" as const },
  ]

  const comparables = [
    { id: "comp-1", name: "Aaron Judge", team: "NYY", similarity: 96 },
    { id: "comp-2", name: "Yordan Alvarez", team: "HOU", similarity: 92 },
    { id: "comp-3", name: "Juan Soto", team: "NYM", similarity: 89 },
  ]

  const strengths = [
    "Elite power with 95th percentile exit velocity",
    "Rare 50-50 potential (HR + SB)",
    "Two-way value in points leagues",
    "Consistent plate discipline",
  ]

  const weaknesses = [
    "High strikeout rate (23%)",
    "Slight platoon split vs LHP",
    "Workload concerns as two-way player",
  ]

  return (
    <div className="flex-1 space-y-6 p-6 lg:p-8">
      {/* Player Hero */}
      <PlayerHero player={player} aiScore={99} grade="A+" />

      {/* AI Scouting Report - Recent Performance Pulse */}
      <ScoutingCard title="Recent Performance Pulse" variant="success">
        <p className="text-foreground">{scoutingReport.recentPerformance}</p>
      </ScoutingCard>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left Column - Verdict + Injury */}
        <div className="space-y-6 lg:col-span-4">
          <ScoutingCard title="Fantasy Verdict">
            <p className="text-foreground">{scoutingReport.fantasyVerdict}</p>
          </ScoutingCard>
          <ScoutingCard title="Injury Status">
            <p className="text-foreground">{scoutingReport.injuryStatus}</p>
          </ScoutingCard>
        </div>

        {/* Right Column - Deep Research */}
        <div className="lg:col-span-8">
          <div className="rounded-xl border border-border bg-card p-4">
            <h3 className="mb-4 font-semibold">Deep Research & Analysis</h3>
            <div className="space-y-4">
              {scoutingReport.deepResearch.map((paragraph, i) => (
                <p key={i} className="text-sm text-muted-foreground leading-relaxed">
                  {paragraph}
                </p>
              ))}
            </div>
            <div className="mt-6">
              <h4 className="mb-3 text-sm font-medium">Recent Stats Breakdown</h4>
              <StatsGrid stats={recentStats} />
            </div>
          </div>
        </div>
      </div>

      {/* Season Stats + Tool Ratings */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-4">
          <h3 className="mb-4 font-semibold">Season Stats</h3>
          <StatsGrid stats={seasonStats} columns={4} />
        </div>
        <ToolRatings ratings={toolRatings} />
      </div>

      {/* Fantasy Points Trend (Placeholder) */}
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

      {/* Bottom Grid - Strengths/Weaknesses + Projections + Comparables */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Strengths & Weaknesses */}
        <div className="rounded-xl border border-border bg-card p-4">
          <h3 className="mb-4 font-semibold">Scouting Report</h3>
          <div className="mb-4">
            <h4 className="mb-2 text-sm font-medium text-emerald-400">Strengths</h4>
            <ul className="space-y-1">
              {strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="material-symbols-outlined text-emerald-400 text-base mt-0.5">
                    check_circle
                  </span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="mb-2 text-sm font-medium text-red-400">Weaknesses</h4>
            <ul className="space-y-1">
              {weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="material-symbols-outlined text-red-400 text-base mt-0.5">
                    warning
                  </span>
                  {w}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <ProjectionsTable projections={projections} />
        <Comparables comparables={comparables} />
      </div>
    </div>
  )
}
