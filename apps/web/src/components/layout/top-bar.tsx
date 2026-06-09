import { SidebarTrigger } from "@/components/ui/sidebar";

export function TopBar() {
  return (
    <header className="flex h-14 shrink-0 items-center gap-2 px-4 transition-[width,height] duration-200 ease-[cubic-bezier(0.23,1,0.32,1)]">
      <SidebarTrigger className="-ml-1" />
      <div className="mx-1 h-4 w-px shrink-0 bg-border" />
      <span className="font-heading text-sm font-semibold">Dashboard</span>
    </header>
  );
}
