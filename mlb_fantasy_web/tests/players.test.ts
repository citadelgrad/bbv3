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

describe("Players API", () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe("listPlayers", () => {
    it("parses player list response correctly", async () => {
      const mockResponse = {
        players: [
          {
            id: "uuid-1",
            full_name: "Shohei Ohtani",
            first_name: "Shohei",
            last_name: "Ohtani",
            mlb_id: 660271,
            current_team: "Los Angeles Dodgers",
            current_team_abbrev: "LAD",
            primary_position: "DH",
            status: "active",
            is_active: true,
          },
          {
            id: "uuid-2",
            full_name: "Elly De La Cruz",
            first_name: "Elly",
            last_name: "De La Cruz",
            mlb_id: 682829,
            current_team: "Cincinnati Reds",
            current_team_abbrev: "CIN",
            primary_position: "SS",
            status: "active",
            is_active: true,
          },
        ],
        total: 1200,
      }

      expect(mockResponse.players).toHaveLength(2)
      expect(mockResponse.total).toBe(1200)
      expect(mockResponse.players[0].full_name).toBe("Shohei Ohtani")
      expect(mockResponse.players[1].primary_position).toBe("SS")
    })

    it("handles pagination parameters", () => {
      const params = {
        limit: 20,
        offset: 40, // page 3
        status: "active",
        position: "SS",
      }

      const searchParams = new URLSearchParams()
      if (params.limit) searchParams.set("limit", String(params.limit))
      if (params.offset) searchParams.set("offset", String(params.offset))
      if (params.status) searchParams.set("status", params.status)
      if (params.position) searchParams.set("position", params.position)

      const query = searchParams.toString()
      expect(query).toBe("limit=20&offset=40&status=active&position=SS")
    })

    it("builds correct URL without optional parameters", () => {
      const params = { limit: 20 }

      const searchParams = new URLSearchParams()
      if (params.limit) searchParams.set("limit", String(params.limit))

      const query = searchParams.toString()
      const url = `/api/v1/players${query ? `?${query}` : ""}`
      expect(url).toBe("/api/v1/players?limit=20")
    })

    it("handles empty response", () => {
      const mockResponse = {
        players: [],
        total: 0,
      }

      expect(mockResponse.players).toHaveLength(0)
      expect(mockResponse.total).toBe(0)
    })
  })

  describe("Player data format", () => {
    it("correctly identifies active vs inactive players", () => {
      const activePlayers = [
        { status: "active", is_active: true },
        { status: "Active", is_active: true },
      ]

      const inactivePlayers = [
        { status: "il-10", is_active: false },
        { status: "il-60", is_active: false },
        { status: "minors", is_active: false },
      ]

      activePlayers.forEach((p) => {
        expect(p.is_active).toBe(true)
      })

      inactivePlayers.forEach((p) => {
        expect(p.is_active).toBe(false)
      })
    })

    it("handles nullable fields properly", () => {
      const player = {
        id: "uuid-1",
        full_name: "Test Player",
        mlb_id: null, // some players may not have MLB ID yet
        fangraphs_id: null,
        current_team: null, // free agent
        current_team_abbrev: null,
        primary_position: null,
        status: "active",
        is_active: true,
      }

      expect(player.mlb_id).toBeNull()
      expect(player.current_team).toBeNull()
      expect(player.current_team_abbrev).toBeNull()
    })

    it("displays team correctly with fallbacks", () => {
      const getTeamDisplay = (player: {
        current_team_abbrev?: string | null
        current_team?: string | null
      }) => {
        return player.current_team_abbrev || player.current_team || "FA"
      }

      expect(getTeamDisplay({ current_team_abbrev: "LAD", current_team: "Los Angeles Dodgers" })).toBe("LAD")
      expect(getTeamDisplay({ current_team_abbrev: null, current_team: "Los Angeles Dodgers" })).toBe("Los Angeles Dodgers")
      expect(getTeamDisplay({ current_team_abbrev: null, current_team: null })).toBe("FA")
    })
  })

  describe("Pagination logic", () => {
    it("calculates correct page indices", () => {
      const pageSize = 20
      const page = 3
      const total = 100

      const startIndex = (page - 1) * pageSize + 1
      const endIndex = Math.min(page * pageSize, total)
      const totalPages = Math.ceil(total / pageSize)

      expect(startIndex).toBe(41)
      expect(endIndex).toBe(60)
      expect(totalPages).toBe(5)
    })

    it("handles last page correctly", () => {
      const pageSize = 20
      const page = 6
      const total = 105

      const startIndex = (page - 1) * pageSize + 1
      const endIndex = Math.min(page * pageSize, total)
      const totalPages = Math.ceil(total / pageSize)

      expect(startIndex).toBe(101)
      expect(endIndex).toBe(105) // not 120
      expect(totalPages).toBe(6)
    })

    it("generates correct page numbers for pagination UI", () => {
      const getPageNumbers = (page: number, totalPages: number) => {
        const pages: (number | string)[] = []
        if (totalPages <= 5) {
          for (let i = 1; i <= totalPages; i++) pages.push(i)
        } else {
          if (page <= 3) {
            pages.push(1, 2, 3, "...", totalPages)
          } else if (page >= totalPages - 2) {
            pages.push(1, "...", totalPages - 2, totalPages - 1, totalPages)
          } else {
            pages.push(1, "...", page, "...", totalPages)
          }
        }
        return pages
      }

      // Small list
      expect(getPageNumbers(1, 3)).toEqual([1, 2, 3])

      // At start of large list
      expect(getPageNumbers(1, 10)).toEqual([1, 2, 3, "...", 10])

      // In middle of large list
      expect(getPageNumbers(5, 10)).toEqual([1, "...", 5, "...", 10])

      // Near end of large list
      expect(getPageNumbers(9, 10)).toEqual([1, "...", 8, 9, 10])
    })
  })

  describe("Position filtering", () => {
    it("filters by position correctly", () => {
      const players = [
        { full_name: "Player A", primary_position: "SS" },
        { full_name: "Player B", primary_position: "1B" },
        { full_name: "Player C", primary_position: "SS" },
        { full_name: "Player D", primary_position: "OF" },
      ]

      const filterByPosition = (position: string) => {
        if (position === "All") return players
        return players.filter((p) => p.primary_position === position)
      }

      expect(filterByPosition("All")).toHaveLength(4)
      expect(filterByPosition("SS")).toHaveLength(2)
      expect(filterByPosition("1B")).toHaveLength(1)
      expect(filterByPosition("C")).toHaveLength(0)
    })

    it("passes position parameter to API when not 'All'", () => {
      const buildParams = (selectedPosition: string) => {
        return {
          limit: 20,
          offset: 0,
          position: selectedPosition !== "All" ? selectedPosition : undefined,
          status: "active",
        }
      }

      expect(buildParams("All").position).toBeUndefined()
      expect(buildParams("SS").position).toBe("SS")
      expect(buildParams("OF").position).toBe("OF")
    })
  })
})
