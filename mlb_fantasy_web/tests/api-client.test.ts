import { describe, it, expect, vi, beforeEach } from "vitest"
import { ApiError } from "@/lib/api/client"

describe("ApiError", () => {
  it("extracts message from error.error.message", () => {
    const error = new ApiError(400, {
      error: { code: "BAD_REQUEST", message: "Invalid request" },
    })
    expect(error.message).toBe("Invalid request")
    expect(error.status).toBe(400)
    expect(error.code).toBe("BAD_REQUEST")
  })

  it("extracts message from error.detail (string)", () => {
    const error = new ApiError(404, {
      detail: "Player not found in registry",
    })
    expect(error.message).toBe("Player not found in registry")
    expect(error.status).toBe(404)
  })

  it("extracts message from error.detail (array - FastAPI validation)", () => {
    const error = new ApiError(422, {
      detail: [
        {
          type: "uuid_parsing",
          loc: ["path", "player_id"],
          msg: "Input should be a valid UUID",
          input: "2",
        },
      ],
    })
    expect(error.message).toBe("Input should be a valid UUID")
    expect(error.status).toBe(422)
  })

  it("extracts message from error.message", () => {
    const error = new ApiError(500, {
      message: "Internal server error",
    })
    expect(error.message).toBe("Internal server error")
    expect(error.status).toBe(500)
  })

  it("defaults to 'An error occurred' when no message found", () => {
    const error = new ApiError(500, {})
    expect(error.message).toBe("An error occurred")
  })

  it("stores raw data for special cases", () => {
    const rawData = {
      status: "ambiguous",
      candidates: [{ id: "1", full_name: "Player 1" }],
    }
    const error = new ApiError(300, rawData)
    expect(error.data).toEqual(rawData)
  })

  it("handles multiple validation errors and uses first message", () => {
    const error = new ApiError(422, {
      detail: [
        { msg: "First error" },
        { msg: "Second error" },
      ],
    })
    expect(error.message).toBe("First error")
  })

  it("handles validation error with missing msg", () => {
    const error = new ApiError(422, {
      detail: [{ type: "error" }],
    })
    expect(error.message).toBe("Validation error")
  })
})

describe("UUID validation", () => {
  const isValidUUID = (str: string) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    return uuidRegex.test(str)
  }

  it("validates correct UUID format", () => {
    expect(isValidUUID("20139aea-42c7-4040-b3f1-97a8432c39c0")).toBe(true)
    expect(isValidUUID("550e8400-e29b-41d4-a716-446655440000")).toBe(true)
  })

  it("rejects invalid UUIDs", () => {
    expect(isValidUUID("1")).toBe(false)
    expect(isValidUUID("2")).toBe(false)
    expect(isValidUUID("abc")).toBe(false)
    expect(isValidUUID("20139aea-42c7-4040-b3f1")).toBe(false) // Too short
    expect(isValidUUID("20139aea42c740403f197a8432c39c0")).toBe(false) // No dashes
  })

  it("is case insensitive", () => {
    expect(isValidUUID("20139AEA-42C7-4040-B3F1-97A8432C39C0")).toBe(true)
  })
})
