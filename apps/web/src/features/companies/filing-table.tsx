import { CheckCircle2, Download, ExternalLink, Loader2 } from "lucide-react";
import { useState } from "react";
import type { Filing } from "@/api";
import { downloadFilingArtifact, getCompanyFilings } from "@/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formBadgeVariant(form: string) {
  if (form.startsWith("10-K")) return "default" as const;
  if (form.startsWith("10-Q")) return "secondary" as const;
  if (form.startsWith("8-K")) return "outline" as const;
  return "outline" as const;
}

interface FilingTableProps {
  ticker: string;
  filings: Filing[];
  loading?: boolean;
  onFilingsChange: (filings: Filing[]) => void;
}

export function FilingTable({ ticker, filings, loading, onFilingsChange }: FilingTableProps) {
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  async function handleDownload(filing: Filing) {
    setDownloadingId(filing.id);
    try {
      await downloadFilingArtifact(ticker, filing.id);
      const refreshed = await getCompanyFilings(ticker);
      onFilingsChange(refreshed);
    } finally {
      setDownloadingId(null);
    }
  }

  if (loading) {
    return (
      <div className="space-y-2">
        {[0, 1, 2, 3, 4].map((n) => (
          <Skeleton key={`loading-skeleton-${n}`} className="h-10 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (filings.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-12 text-center">
        <p className="text-sm text-muted-foreground">
          No filings synced yet. Search and sync a company to get started.
        </p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-20">Form</TableHead>
          <TableHead className="w-28">Filed</TableHead>
          <TableHead>Document</TableHead>
          <TableHead className="w-28 text-right">Artifact</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {filings.slice(0, 20).map((filing) => (
          <TableRow key={filing.id}>
            <TableCell>
              <Badge variant={formBadgeVariant(filing.form)} className="font-mono text-[10px]">
                {filing.form}
              </Badge>
            </TableCell>
            <TableCell className="text-xs text-muted-foreground">
              {filing.filing_date ?? "—"}
            </TableCell>
            <TableCell className="max-w-xs">
              {filing.source_url ? (
                <a
                  href={filing.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-sm underline-offset-2 hover:underline"
                >
                  <span className="truncate">
                    {filing.primary_document ?? filing.accession_number}
                  </span>
                  <ExternalLink className="size-3 shrink-0 text-muted-foreground" />
                </a>
              ) : (
                <span className="text-sm text-muted-foreground">
                  {filing.primary_document ?? filing.accession_number}
                </span>
              )}
            </TableCell>
            <TableCell className="text-right">
              {filing.artifact ? (
                <span
                  className="inline-flex items-center gap-1.5 text-xs text-emerald-400"
                  title={filing.artifact.sha256}
                >
                  <CheckCircle2 className="size-3.5" />
                  {formatBytes(filing.artifact.byte_size)}
                </span>
              ) : (
                <Button
                  variant="ghost"
                  size="xs"
                  disabled={downloadingId === filing.id}
                  onClick={() => handleDownload(filing)}
                >
                  {downloadingId === filing.id ? (
                    <Loader2 className="size-3 animate-spin" />
                  ) : (
                    <Download className="size-3" />
                  )}
                  Store
                </Button>
              )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
