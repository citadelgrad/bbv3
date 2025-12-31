"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Avatar } from "@/components/ui/avatar"

interface NavItem {
  label: string
  href: string
  icon: string
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: "dashboard" },
  { label: "My Teams", href: "/teams", icon: "groups" },
  { label: "Scouting Reports", href: "/scout", icon: "psychology" },
  { label: "Waiver Wire", href: "/waiver-wire", icon: "person_search" },
  { label: "Settings", href: "/settings", icon: "settings" },
]

interface SidebarProps {
  user?: {
    email?: string | null
    user_metadata?: {
      full_name?: string
      avatar_url?: string
    }
  } | null
  className?: string
}

export function Sidebar({ user, className }: SidebarProps) {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = React.useState(false)

  const userName = user?.user_metadata?.full_name || user?.email?.split("@")[0] || "Manager"
  const userEmail = user?.email || ""

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300",
        collapsed ? "w-16" : "w-64",
        className
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-4">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/20 text-primary">
          <span className="material-symbols-outlined text-xl">sports_baseball</span>
        </div>
        {!collapsed && (
          <span className="text-lg font-bold text-sidebar-foreground">Fantasy AI Scout</span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <span className="material-symbols-outlined text-xl">{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* User Profile */}
      <div className="border-t border-sidebar-border p-3">
        <div className="flex items-center gap-3 rounded-lg px-3 py-2">
          <Avatar
            src={user?.user_metadata?.avatar_url}
            alt={userName}
            size="sm"
          />
          {!collapsed && (
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium text-sidebar-foreground">
                {userName}
              </p>
              <p className="truncate text-xs text-muted-foreground">{userEmail}</p>
            </div>
          )}
        </div>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex h-10 items-center justify-center border-t border-sidebar-border text-muted-foreground hover:text-sidebar-foreground"
      >
        <span className="material-symbols-outlined text-xl">
          {collapsed ? "chevron_right" : "chevron_left"}
        </span>
      </button>
    </aside>
  )
}
