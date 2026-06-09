import { useState } from "react";
import { AppShell, type Page } from "@/components/layout/app-shell";
import { HomePage } from "@/features/home/home-page";

export function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");

  return (
    <AppShell currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === "dashboard" && <HomePage />}
      {currentPage === "search" && <HomePage />}
      {currentPage === "filings" && <HomePage />}
      {currentPage === "activity" && <HomePage />}
    </AppShell>
  );
}
