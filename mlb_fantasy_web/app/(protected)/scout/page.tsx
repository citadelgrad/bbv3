"use client";

import { useState } from "react";
import { SearchForm } from "@/components/scout/search-form";
import { ReportCard } from "@/components/scout/report-card";
import { Card, CardContent } from "@/components/ui/card";
import {
  researchPlayer,
  getJobStatus,
} from "@/lib/api/scouting";
import type { ScoutingReport } from "@/lib/api/types";
import { toast } from "sonner";

type Status = "idle" | "loading" | "polling" | "complete" | "error";

export default function ScoutPage() {
  const [status, setStatus] = useState<Status>("idle");
  const [report, setReport] = useState<ScoutingReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollingMessage, setPollingMessage] = useState<string>("");

  async function handleSearch(playerName: string) {
    setStatus("loading");
    setError(null);
    setReport(null);

    try {
      const response = await researchPlayer(playerName);

      if (response.status === "cached" || response.status === "generated") {
        // Got a report immediately (cached)
        setReport(response.report);
        setStatus("complete");
        toast.success(`Found cached report for ${playerName}`);
      } else if (response.status === "pending") {
        // Need to poll for completion
        setStatus("polling");
        setPollingMessage(`Researching ${playerName}...`);
        await pollForCompletion(response.job_id, playerName);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Research failed";
      setError(message);
      setStatus("error");
      toast.error(message);
    }
  }

  async function pollForCompletion(jobId: string, playerName: string) {
    const maxAttempts = 60; // 2 minutes max
    const intervalMs = 2000;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const jobStatus = await getJobStatus(jobId);

        if (jobStatus.status === "success" && jobStatus.result) {
          // Convert job result to ScoutingReport format
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
          };
          setReport(reportData);
          setStatus("complete");
          toast.success(`Report generated for ${playerName}`);
          return;
        }

        if (jobStatus.status === "failed" || jobStatus.status === "failure") {
          throw new Error(
            jobStatus.error_message || jobStatus.error || "Research job failed"
          );
        }

        // Still running, update message and wait
        setPollingMessage(
          `Researching ${playerName}... (${Math.floor((attempt * intervalMs) / 1000)}s)`
        );
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
      } catch (err) {
        const message = err instanceof Error ? err.message : "Polling failed";
        setError(message);
        setStatus("error");
        toast.error(message);
        return;
      }
    }

    // Timeout
    setError("Research timed out. Please try again.");
    setStatus("error");
    toast.error("Research timed out");
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Player Scout</h1>
        <p className="text-muted-foreground">
          Deep research any MLB player for fantasy insights
        </p>
      </div>

      {/* Search Form */}
      <Card>
        <CardContent className="pt-6">
          <SearchForm
            onSearch={handleSearch}
            isLoading={status === "loading" || status === "polling"}
          />
        </CardContent>
      </Card>

      {/* Status Messages */}
      {status === "polling" && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              <p className="text-muted-foreground">{pollingMessage}</p>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Deep research may take 30-60 seconds to complete...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {status === "error" && error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Report Display */}
      {status === "complete" && report && <ReportCard report={report} />}
    </div>
  );
}
