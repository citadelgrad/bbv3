"use client";

import ReactMarkdown from "react-markdown";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ScoutingReport, GroundingSource } from "@/lib/api/types";

interface ReportCardProps {
  report: ScoutingReport;
}

function SourcesList({ sources }: { sources: GroundingSource[] }) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-6 pt-4 border-t">
      <h4 className="text-sm font-medium text-muted-foreground mb-2">Sources</h4>
      <ul className="text-sm space-y-1">
        {sources.map((source, index) => (
          <li key={index}>
            <a
              href={source.uri}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {source.title}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ReportCard({ report }: ReportCardProps) {
  const createdAt = new Date(report.created_at).toLocaleString();
  const expiresAt = new Date(report.expires_at).toLocaleString();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold">{report.player_name}</h2>
        <p className="text-muted-foreground">
          Generated {createdAt} | Expires {expiresAt}
        </p>
      </div>

      {/* Summary Card */}
      <Card className="bg-emerald-50 border-emerald-200">
        <CardContent className="pt-6">
          <p className="text-lg">{report.summary}</p>
        </CardContent>
      </Card>

      {/* Main Content Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Fantasy Outlook */}
          <Card>
            <CardHeader>
              <CardTitle>Fantasy Outlook</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{report.fantasy_outlook}</p>
            </CardContent>
          </Card>

          {/* Injury Status */}
          <Card>
            <CardHeader>
              <CardTitle>Injury Status</CardTitle>
            </CardHeader>
            <CardContent>
              <p
                className={
                  report.injury_status.toLowerCase() === "healthy"
                    ? "text-green-600 font-medium"
                    : "text-amber-600"
                }
              >
                {report.injury_status}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Recent Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Stats</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <ReactMarkdown>{report.recent_stats}</ReactMarkdown>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Detailed Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Deep Research Analysis</CardTitle>
        </CardHeader>
        <CardContent className="prose max-w-none">
          <ReactMarkdown>{report.detailed_analysis}</ReactMarkdown>
        </CardContent>
      </Card>

      {/* Sources & Cost */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <SourcesList sources={report.sources} />
            </div>
            <div className="text-right text-sm text-muted-foreground">
              <p>Tokens: {report.token_usage.total_tokens.toLocaleString()}</p>
              <p>Cost: {report.token_usage.estimated_cost}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
