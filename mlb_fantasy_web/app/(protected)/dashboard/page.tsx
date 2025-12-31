"use client"

import { Button } from "@/components/ui/button"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { ActionCard } from "@/components/dashboard/action-card"
import { RosterTable } from "@/components/dashboard/roster-table"
import { MatchupWidget } from "@/components/dashboard/matchup-widget"
import { StandingsWidget } from "@/components/dashboard/standings-widget"
import { NewsFeed } from "@/components/dashboard/news-feed"
import { TeamSelector } from "@/components/dashboard/team-selector"
import {
  mockRoster,
  mockStandings,
  mockNews,
  mockMatchup,
  mockKpis,
  mockPlayers,
} from "@/lib/mock-data"

export default function DashboardPage() {
  const mockTeams = [
    { id: "team-1", name: "Big League Chewers" },
    { id: "team-2", name: "Dynasty Legends" },
  ]

  return (
    <div className="flex-1 space-y-6 p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Welcome back, Manager</h1>
          <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <span className="material-symbols-outlined text-base text-emerald-500">sync</span>
            <span>Last synced 5 minutes ago</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <TeamSelector
            teams={mockTeams}
            selectedTeamId="team-1"
            className="w-48"
          />
          <Button variant="outline" size="sm">
            <span className="material-symbols-outlined mr-2 text-lg">sync</span>
            Sync Now
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <KpiCard
          title="Overall AI Grade"
          value={mockKpis.aiGrade.value}
          trend={mockKpis.aiGrade.trend}
          icon="insights"
        />
        <KpiCard
          title="Current League Rank"
          value={mockKpis.leagueRank.value}
          trend="+1 Spot"
          icon="leaderboard"
        />
        <KpiCard
          title="Projected Finish"
          value={mockKpis.projectedFinish.value}
          trendLabel={`AI Confidence: ${mockKpis.projectedFinish.confidence}`}
          icon="trending_up"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Action Center + Roster */}
        <div className="space-y-6 lg:col-span-2">
          {/* AI Action Center */}
          <div>
            <h2 className="mb-4 flex items-center gap-2 font-semibold">
              <span className="material-symbols-outlined text-primary">auto_awesome</span>
              AI Action Center
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <ActionCard
                title="Top Waiver Target"
                icon="person_add"
                badge="94% Match"
                badgeVariant="success"
                playerName={mockPlayers[5].fullName}
                playerTeam={`${mockPlayers[5].position} - ${mockPlayers[5].teamAbbrev}`}
                actionLabel="View Full Analysis"
                actionHref={`/player/${mockPlayers[5].id}`}
              />
              <ActionCard
                title="Sell High Alert"
                subtitle="Value Peak"
                icon="trending_down"
                badge="Trade Window"
                badgeVariant="warning"
                playerName={mockPlayers[4].fullName}
                playerTeam={`${mockPlayers[4].position} - ${mockPlayers[4].teamAbbrev}`}
                actionLabel="Find Trade Partners"
                actionHref="/trades"
              />
            </div>
          </div>

          {/* Roster Pulse */}
          <RosterTable players={mockRoster.slice(0, 6)} />
        </div>

        {/* Right Column - Matchup + Standings + News */}
        <div className="space-y-6">
          <MatchupWidget
            userScore={mockMatchup.userScore}
            opponentScore={mockMatchup.opponentScore}
            opponentName={mockMatchup.opponentName}
            winProbability={mockMatchup.winProbability}
          />
          <StandingsWidget standings={mockStandings} />
          <NewsFeed news={mockNews} />
        </div>
      </div>
    </div>
  )
}
