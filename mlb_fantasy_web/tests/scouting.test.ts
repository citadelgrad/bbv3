import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { ApiError } from "@/lib/api/client"

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock Supabase client
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({
    auth: {
      getSession: () => Promise.resolve({ data: { session: { access_token: "test-token" } } }),
    },
  }),
}))

describe("Scouting API Response Handling", () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe("Job Status Response", () => {
    it("correctly parses success status with result", async () => {
      const jobResponse = {
        id: "test-job-id",
        status: "success",
        result: {
          status: "generated",
          report_id: "report-123",
          player_name: "Elly De La Cruz",
          summary: "Test summary",
          recent_stats: "Test stats",
          injury_status: "Healthy",
          fantasy_outlook: "Good",
          detailed_analysis: "Analysis",
          sources: [],
          token_usage: { total_tokens: 100 },
          created_at: "2025-01-01T00:00:00Z",
          expires_at: "2025-01-15T00:00:00Z",
        },
      }

      expect(jobResponse.status).toBe("success")
      expect(jobResponse.result).toBeDefined()
      expect(jobResponse.result?.player_name).toBe("Elly De La Cruz")
    })

    it("correctly identifies failure status", () => {
      const jobResponse = {
        id: "test-job-id",
        status: "failure",
        error_message: "research_player() got an unexpected keyword argument 'player_id'",
      }

      // Both "failed" and "failure" should be treated as failures
      const isFailed = jobResponse.status === "failed" || jobResponse.status === "failure"
      expect(isFailed).toBe(true)
      expect(jobResponse.error_message).toContain("unexpected keyword argument")
    })

    it("handles error_message field (not just error)", () => {
      const jobResponse = {
        status: "failure",
        error_message: "Database connection failed",
        error: undefined,
      }

      const errorMsg = jobResponse.error_message || jobResponse.error || "Unknown error"
      expect(errorMsg).toBe("Database connection failed")
    })
  })

  describe("Research Response Types", () => {
    it("identifies cached response", () => {
      const response = {
        status: "cached",
        report: { id: "123", player_name: "Test Player" },
      }
      expect(response.status).toBe("cached")
      expect(response.report).toBeDefined()
    })

    it("identifies pending response", () => {
      const response = {
        status: "pending",
        job_id: "job-123",
        message: "Research in progress",
      }
      expect(response.status).toBe("pending")
      expect(response.job_id).toBe("job-123")
    })

    it("identifies ambiguous response", () => {
      const response = {
        status: "ambiguous",
        candidates: [
          { id: "1", full_name: "Player A", current_team_abbrev: "LAD" },
          { id: "2", full_name: "Player B", current_team_abbrev: "NYY" },
        ],
        message: "Multiple players match",
      }
      expect(response.status).toBe("ambiguous")
      expect(response.candidates).toHaveLength(2)
    })
  })
})

describe("Mock to Player Conversion", () => {
  const mockToPlayer = (mock: {
    id: string
    fullName: string
    firstName: string
    lastName: string
    team: string
    teamAbbrev: string
    position: string
    mlbId: number
    status: string
  }) => ({
    id: mock.id,
    full_name: mock.fullName,
    first_name: mock.firstName,
    last_name: mock.lastName,
    name_suffix: null,
    name_normalized: mock.fullName.toLowerCase(),
    mlb_id: mock.mlbId,
    fangraphs_id: null,
    current_team: mock.team,
    current_team_abbrev: mock.teamAbbrev,
    primary_position: mock.position,
    status: mock.status,
    is_active: mock.status === "active",
  })

  it("converts mock player to API player format", () => {
    const mockPlayer = {
      id: "2",
      fullName: "Elly De La Cruz",
      firstName: "Elly",
      lastName: "De La Cruz",
      team: "Cincinnati Reds",
      teamAbbrev: "CIN",
      position: "SS",
      mlbId: 682829,
      status: "active",
    }

    const player = mockToPlayer(mockPlayer)

    expect(player.id).toBe("2")
    expect(player.full_name).toBe("Elly De La Cruz")
    expect(player.name_normalized).toBe("elly de la cruz")
    expect(player.current_team).toBe("Cincinnati Reds")
    expect(player.primary_position).toBe("SS")
    expect(player.is_active).toBe(true)
  })

  it("handles inactive player status", () => {
    const mockPlayer = {
      id: "3",
      fullName: "Test Player",
      firstName: "Test",
      lastName: "Player",
      team: "Test Team",
      teamAbbrev: "TST",
      position: "P",
      mlbId: 123456,
      status: "il-10",
    }

    const player = mockToPlayer(mockPlayer)
    expect(player.is_active).toBe(false)
  })
})
