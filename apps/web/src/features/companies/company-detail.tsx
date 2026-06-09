import { Building2, Calendar, Globe, Hash } from "lucide-react";
import type { Company } from "@/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CompanyDetailProps {
  company: Company;
}

export function CompanyDetail({ company }: CompanyDetailProps) {
  const fields = [
    { icon: Hash, label: "CIK", value: company.cik_padded },
    { icon: Globe, label: "Exchange", value: company.exchange ?? "N/A" },
    { icon: Building2, label: "SIC", value: company.sic ?? "N/A" },
    { icon: Calendar, label: "Fiscal Year End", value: company.fiscal_year_end ?? "N/A" },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="size-4" />
          {company.ticker}
          <span className="text-base font-normal text-muted-foreground">{company.name}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {fields.map((f) => (
            <div
              key={f.label}
              className="flex items-center gap-2 rounded-lg border border-border/50 px-3 py-2"
            >
              <f.icon className="size-3.5 shrink-0 text-muted-foreground" />
              <div className="min-w-0">
                <p className="text-[11px] text-muted-foreground">{f.label}</p>
                <p className="truncate text-sm font-medium">{f.value}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
