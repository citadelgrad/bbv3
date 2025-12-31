// Mock data for Fantasy AI Scout frontend
// This allows the UI to be functional before all backend APIs are implemented

export interface MockPlayer {
  id: string
  fullName: string
  firstName: string
  lastName: string
  team: string
  teamAbbrev: string
  position: string
  mlbId: number
  status: "active" | "dtd" | "il-10" | "il-15" | "il-60"
  imageUrl?: string
  stats: {
    avg: number
    hr: number
    rbi: number
    sb: number
    ops: number
  }
  outlook?: number // 0-100 score
  trend?: number // percentage change
}

export interface MockTeam {
  id: string
  name: string
  leagueName: string
  rank: number
  record: { wins: number; losses: number; ties: number }
  points: number
}

export interface MockLeagueStanding {
  rank: number
  teamName: string
  managerName: string
  record: string
  points: number
  isUser?: boolean
}

export interface MockNewsItem {
  id: string
  playerName: string
  headline: string
  timestamp: string
  type: "injury" | "transaction" | "performance"
}

export interface MockRecommendation {
  player: MockPlayer
  matchScore: number
  reason: string
  projections: {
    hr?: number
    sb?: number
    avg?: number
    era?: number
    k9?: number
  }
}

// Sample players
export const mockPlayers: MockPlayer[] = [
  {
    id: "1",
    fullName: "Shohei Ohtani",
    firstName: "Shohei",
    lastName: "Ohtani",
    team: "Los Angeles Dodgers",
    teamAbbrev: "LAD",
    position: "DH",
    mlbId: 660271,
    status: "active",
    stats: { avg: 0.304, hr: 54, rbi: 130, sb: 59, ops: 1.036 },
    outlook: 95,
    trend: 8.2,
  },
  {
    id: "2",
    fullName: "Elly De La Cruz",
    firstName: "Elly",
    lastName: "De La Cruz",
    team: "Cincinnati Reds",
    teamAbbrev: "CIN",
    position: "SS",
    mlbId: 682829,
    status: "active",
    stats: { avg: 0.262, hr: 25, rbi: 76, sb: 67, ops: 0.794 },
    outlook: 88,
    trend: 12.5,
  },
  {
    id: "3",
    fullName: "Bobby Miller",
    firstName: "Bobby",
    lastName: "Miller",
    team: "Los Angeles Dodgers",
    teamAbbrev: "LAD",
    position: "SP",
    mlbId: 676272,
    status: "active",
    stats: { avg: 0, hr: 0, rbi: 0, sb: 0, ops: 0 },
    outlook: 82,
    trend: 5.1,
  },
  {
    id: "4",
    fullName: "Jhoan Duran",
    firstName: "Jhoan",
    lastName: "Duran",
    team: "Minnesota Twins",
    teamAbbrev: "MIN",
    position: "RP",
    mlbId: 661395,
    status: "active",
    stats: { avg: 0, hr: 0, rbi: 0, sb: 0, ops: 0 },
    outlook: 79,
    trend: -2.3,
  },
  {
    id: "5",
    fullName: "Juan Soto",
    firstName: "Juan",
    lastName: "Soto",
    team: "New York Mets",
    teamAbbrev: "NYM",
    position: "RF",
    mlbId: 665742,
    status: "active",
    stats: { avg: 0.288, hr: 41, rbi: 109, sb: 7, ops: 0.989 },
    outlook: 91,
    trend: -1.8,
  },
  {
    id: "6",
    fullName: "Tarik Skubal",
    firstName: "Tarik",
    lastName: "Skubal",
    team: "Detroit Tigers",
    teamAbbrev: "DET",
    position: "SP",
    mlbId: 669373,
    status: "active",
    stats: { avg: 0, hr: 0, rbi: 0, sb: 0, ops: 0 },
    outlook: 94,
    trend: 15.2,
  },
  {
    id: "7",
    fullName: "Gunnar Henderson",
    firstName: "Gunnar",
    lastName: "Henderson",
    team: "Baltimore Orioles",
    teamAbbrev: "BAL",
    position: "SS",
    mlbId: 683002,
    status: "active",
    stats: { avg: 0.282, hr: 37, rbi: 92, sb: 12, ops: 0.893 },
    outlook: 89,
    trend: 4.7,
  },
  {
    id: "8",
    fullName: "Ronald Acuna Jr.",
    firstName: "Ronald",
    lastName: "Acuna Jr.",
    team: "Atlanta Braves",
    teamAbbrev: "ATL",
    position: "RF",
    mlbId: 660670,
    status: "il-60",
    stats: { avg: 0.217, hr: 4, rbi: 14, sb: 7, ops: 0.616 },
    outlook: 45,
    trend: -35.2,
  },
  {
    id: "9",
    fullName: "Corbin Carroll",
    firstName: "Corbin",
    lastName: "Carroll",
    team: "Arizona Diamondbacks",
    teamAbbrev: "ARI",
    position: "CF",
    mlbId: 682998,
    status: "dtd",
    stats: { avg: 0.228, hr: 16, rbi: 57, sb: 24, ops: 0.703 },
    outlook: 62,
    trend: -8.4,
  },
  {
    id: "10",
    fullName: "Spencer Strider",
    firstName: "Spencer",
    lastName: "Strider",
    team: "Atlanta Braves",
    teamAbbrev: "ATL",
    position: "SP",
    mlbId: 675911,
    status: "il-15",
    stats: { avg: 0, hr: 0, rbi: 0, sb: 0, ops: 0 },
    outlook: 55,
    trend: -18.9,
  },
]

// Sample roster (user's team)
export const mockRoster: MockPlayer[] = mockPlayers.slice(0, 8)

// Sample league standings
export const mockStandings: MockLeagueStanding[] = [
  { rank: 1, teamName: "Dinger Dynasty", managerName: "Mike T.", record: "18-6", points: 2847 },
  { rank: 2, teamName: "Big League Chewers", managerName: "You", record: "16-8", points: 2654, isUser: true },
  { rank: 3, teamName: "Base Stealers", managerName: "Sarah K.", record: "15-9", points: 2512 },
  { rank: 4, teamName: "Ace Ventura", managerName: "Tom B.", record: "14-10", points: 2398 },
  { rank: 5, teamName: "Bat Attitudes", managerName: "Lisa M.", record: "12-12", points: 2156 },
  { rank: 6, teamName: "Diamond Dogs", managerName: "Chris P.", record: "10-14", points: 1987 },
]

// Sample news
export const mockNews: MockNewsItem[] = [
  {
    id: "1",
    playerName: "Ronald Acuna Jr.",
    headline: "Expected to begin rehab assignment next week",
    timestamp: "2h ago",
    type: "injury",
  },
  {
    id: "2",
    playerName: "Tarik Skubal",
    headline: "Named AL Pitcher of the Month for June",
    timestamp: "4h ago",
    type: "performance",
  },
  {
    id: "3",
    playerName: "Juan Soto",
    headline: "Trade rumors heating up ahead of deadline",
    timestamp: "6h ago",
    type: "transaction",
  },
]

// Sample recommendations for waiver wire
export const mockRecommendations: MockRecommendation[] = [
  {
    player: mockPlayers[1], // Elly De La Cruz
    matchScore: 98,
    reason: "Elite speed + power combo. Breakout candidate with 5-category upside.",
    projections: { hr: 3, sb: 8, avg: 0.275 },
  },
  {
    player: mockPlayers[2], // Bobby Miller
    matchScore: 94,
    reason: "High K upside in favorable matchups. Projected ace stuff.",
    projections: { k9: 11.2, era: 3.15 },
  },
  {
    player: mockPlayers[3], // Jhoan Duran
    matchScore: 91,
    reason: "Elite closer with 0.00 ERA over last 14 days. Saves leader.",
    projections: { era: 0.0 },
  },
]

// Sample user team
export const mockUserTeam: MockTeam = {
  id: "team-1",
  name: "Big League Chewers",
  leagueName: "The Show 2024",
  rank: 2,
  record: { wins: 16, losses: 8, ties: 0 },
  points: 2654,
}

// Weekly matchup data
export const mockMatchup = {
  userScore: 482,
  opponentScore: 410,
  opponentName: "Dinger Dynasty",
  winProbability: 72,
  categories: {
    batting: { user: 245, opponent: 220 },
    pitching: { user: 237, opponent: 190 },
  },
}

// KPI data for dashboard
export const mockKpis = {
  aiGrade: { value: "B+", trend: 2.4, description: "Overall AI Grade" },
  leagueRank: { value: "2nd", trend: 1, description: "Current League Rank" },
  projectedFinish: { value: "1st", confidence: "High", description: "AI Projected Finish" },
}

// Position filter options
export const positions = ["All", "C", "1B", "2B", "3B", "SS", "OF", "SP", "RP"] as const
export type Position = (typeof positions)[number]

// Status display helpers
export const statusLabels: Record<MockPlayer["status"], string> = {
  active: "Active",
  dtd: "Day-to-Day",
  "il-10": "IL-10",
  "il-15": "IL-15",
  "il-60": "IL-60",
}

export const statusColors: Record<MockPlayer["status"], string> = {
  active: "success",
  dtd: "warning",
  "il-10": "destructive",
  "il-15": "destructive",
  "il-60": "destructive",
}
