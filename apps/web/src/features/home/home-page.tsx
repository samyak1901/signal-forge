import { CircuitBoard, Database, FileArchive, Layers, RefreshCw } from "lucide-react";
import { useState } from "react";
import type { Company, Filing } from "@/api";
import { getCompanyFilings, syncCompany } from "@/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CompanyDetail } from "@/features/companies/company-detail";
import { CompanySearch } from "@/features/companies/company-search";
import { FilingTable } from "@/features/companies/filing-table";
import { cn } from "@/lib/utils";

const pipelineSteps = [
  "Resolve ticker to CIK",
  "Fetch SEC submissions",
  "Persist filing metadata",
  "Download primary filing",
  "Extract sections",
  "Generate citations",
];

const platformCards = [
  {
    icon: Database,
    label: "Postgres",
    description: "Filing metadata and company records",
  },
  {
    icon: FileArchive,
    label: "MinIO",
    description: "Raw SEC document artifacts",
  },
  {
    icon: CircuitBoard,
    label: "Qdrant",
    description: "Vector embeddings for RAG",
  },
];

export function HomePage() {
  const [company, setCompany] = useState<Company | null>(null);
  const [filings, setFilings] = useState<Filing[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  async function handleSelectTicker(ticker: string) {
    setLoading(true);
    setStatus(`Syncing ${ticker}...`);
    try {
      const result = await syncCompany(ticker);
      const syncedFilings = await getCompanyFilings(ticker);
      setCompany(result.company);
      setFilings(syncedFilings);
      setStatus(`Synced ${result.filings_synced} filings for ${ticker}`);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleResync() {
    if (!company) return;
    setSyncing(true);
    try {
      const result = await syncCompany(company.ticker);
      const syncedFilings = await getCompanyFilings(company.ticker);
      setFilings(syncedFilings);
      setStatus(`Re-synced ${result.filings_synced} filings`);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-semibold">Research Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Source-backed public-company research cockpit
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left column: search + company detail */}
        <div className="space-y-6 lg:col-span-2">
          <CompanySearch onSelect={handleSelectTicker} />

          {company && <CompanyDetail company={company} />}

          {/* Filing section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="size-4" />
                  SEC Filings
                </div>
                {company && (
                  <Button variant="outline" size="sm" disabled={syncing} onClick={handleResync}>
                    <RefreshCw className={cn("size-3.5", syncing && "animate-spin")} />
                    Re-sync
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FilingTable
                ticker={company?.ticker ?? ""}
                filings={filings}
                loading={loading}
                onFilingsChange={setFilings}
              />
            </CardContent>
          </Card>

          {/* Status bar */}
          {status && (
            <div className="rounded-lg border border-border/50 bg-muted/30 px-4 py-2">
              <p className="text-xs text-muted-foreground">{status}</p>
            </div>
          )}
        </div>

        {/* Right column: pipeline + platform info */}
        <div className="space-y-6">
          {/* Pipeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CircuitBoard className="size-4" />
                Pipeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-2">
                {pipelineSteps.map((step, i) => (
                  <li key={step} className="flex items-center gap-3 text-sm">
                    <span
                      className={cn(
                        "flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-medium",
                        i <= 3 ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground",
                      )}
                    >
                      {i + 1}
                    </span>
                    <span className={i <= 3 ? "text-foreground" : "text-muted-foreground"}>
                      {step}
                    </span>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>

          {/* Platform */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="size-4" />
                Stack
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {platformCards.map((item) => (
                <div
                  key={item.label}
                  className="flex items-center gap-3 rounded-lg border border-border/50 px-3 py-2.5"
                >
                  <item.icon className="size-4 shrink-0 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.description}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Source chips */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileArchive className="size-4" />
                Sources
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {["10-K", "10-Q", "8-K", "DEF 14A"].map((s) => (
                  <Badge key={s} variant="secondary" className="font-mono text-[10px]">
                    {s}
                  </Badge>
                ))}
                {["Transcripts", "News"].map((s) => (
                  <Badge key={s} variant="outline" className="text-[10px]">
                    {s}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
