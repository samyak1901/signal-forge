import { Activity, BarChart3, FileText, Moon, Search, Sun } from "lucide-react";
import type { ComponentProps } from "react";
import { useState } from "react";
import { BrandLogo } from "@/components/branding/brand-logo";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";

type Page = "dashboard" | "search" | "filings" | "activity";

const navItems: { page: Page; label: string; icon: typeof Search }[] = [
  { page: "dashboard", label: "Dashboard", icon: BarChart3 },
  { page: "search", label: "Search", icon: Search },
  { page: "filings", label: "Filings", icon: FileText },
  { page: "activity", label: "Activity", icon: Activity },
];

const navButtonClass = "h-9 gap-2.5 [&_svg]:size-[1.125rem]";

export function AppSidebar({
  currentPage,
  onNavigate,
  ...props
}: ComponentProps<typeof Sidebar> & {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}) {
  const [theme, setThemeState] = useState<"dark" | "light">(() =>
    document.documentElement.classList.contains("dark") ? "dark" : "light",
  );

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setThemeState(next);
    document.documentElement.classList.toggle("dark", next === "dark");
  }

  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton>
              <BrandLogo variant="icon" className="size-10 text-sm" />
              <div className="grid flex-1 text-left leading-tight">
                <span className="truncate font-heading text-base font-semibold">SignalForge</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
                <SidebarMenuItem key={item.page}>
                  <SidebarMenuButton
                    isActive={currentPage === item.page}
                    tooltip={item.label}
                    className={navButtonClass}
                    onClick={() => onNavigate(item.page)}
                  >
                    <item.icon />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={theme === "dark" ? "Light mode" : "Dark mode"}
              className={navButtonClass}
              onClick={toggleTheme}
            >
              {theme === "dark" ? <Sun /> : <Moon />}
              <span>{theme === "dark" ? "Light mode" : "Dark mode"}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
