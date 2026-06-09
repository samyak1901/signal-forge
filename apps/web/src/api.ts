export interface CompanySearchResult {
  ticker: string;
  cik: number;
  cik_padded: string;
  name: string;
  exchange: string | null;
}

export interface Company {
  id: number;
  ticker: string;
  cik: number;
  cik_padded: string;
  name: string;
  exchange: string | null;
  sic: string | null;
  fiscal_year_end: string | null;
  created_at: string;
  updated_at: string;
}

export interface Filing {
  id: number;
  accession_number: string;
  form: string;
  filing_date: string | null;
  report_date: string | null;
  primary_document: string | null;
  primary_doc_description: string | null;
  source_url: string | null;
}

export interface CompanySyncResponse {
  company: Company;
  filings_synced: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { Accept: "application/json", ...init?.headers },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export function searchCompanies(query: string): Promise<CompanySearchResult[]> {
  const params = new URLSearchParams({ q: query });
  return request<CompanySearchResult[]>(`/api/v1/companies/search?${params}`);
}

export function syncCompany(ticker: string): Promise<CompanySyncResponse> {
  return request<CompanySyncResponse>(`/api/v1/companies/${ticker}/sync`, { method: "POST" });
}

export function getCompanyFilings(ticker: string): Promise<Filing[]> {
  return request<Filing[]>(`/api/v1/companies/${ticker}/filings`);
}
