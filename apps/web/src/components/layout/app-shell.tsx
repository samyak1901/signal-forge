import type { ReactNode } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { TopBar } from "@/components/layout/top-bar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

export type Page = "dashboard" | "search" | "filings" | "activity";

interface AppShellProps {
  children: ReactNode;
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

export function AppShell({ children, currentPage, onNavigate }: AppShellProps) {
  return (
    <SidebarProvider className="h-svh overflow-hidden">
      <AppSidebar currentPage={currentPage} onNavigate={onNavigate} />
      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <TopBar />
        <SidebarInset className="min-h-0 overflow-y-auto">
          <div className="flex min-h-0 flex-1 flex-col">{children}</div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
