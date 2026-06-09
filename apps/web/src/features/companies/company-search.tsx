import { ArrowRight, Loader2, Search } from "lucide-react";
import { useState } from "react";
import type { CompanySearchResult } from "@/api";
import { searchCompanies } from "@/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface CompanySearchProps {
  onSelect: (ticker: string) => void;
}

export function CompanySearch({ onSelect }: CompanySearchProps) {
  const [query, setQuery] = useState("AAPL");
  const [matches, setMatches] = useState<CompanySearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch() {
    const q = query.trim().toUpperCase();
    if (!q) return;
    setLoading(true);
    setError(null);
    try {
      const results = await searchCompanies(q);
      setMatches(results);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="size-4" />
          Company Search
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="Enter ticker symbol..."
            value={query}
            onChange={(e) => setQuery(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <Button onClick={handleSearch} disabled={loading}>
            {loading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
            Search
          </Button>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {matches.length > 0 && (
          <ul className="space-y-1">
            {matches.map((m) => (
              <li key={`${m.ticker}-${m.cik}`}>
                <button
                  type="button"
                  onClick={() => onSelect(m.ticker)}
                  className={cn(
                    "group flex w-full items-center justify-between rounded-lg border border-border/50 px-3 py-2 text-left text-sm transition-colors",
                    "hover:border-border hover:bg-muted/50",
                  )}
                >
                  <div className="min-w-0 flex-1">
                    <span className="font-medium">{m.ticker}</span>
                    <span className="ml-2 text-muted-foreground">{m.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {m.exchange && (
                      <Badge variant="secondary" className="text-[10px]">
                        {m.exchange}
                      </Badge>
                    )}
                    <ArrowRight className="size-3.5 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
