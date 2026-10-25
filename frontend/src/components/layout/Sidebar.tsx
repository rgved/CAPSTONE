import { NavLink } from "react-router-dom";
import Logo from "../brand/Logo";
import {
  Home,
  LayoutDashboard,
  Play,
  ShieldAlert,
  FileText,
  BarChart3
} from "lucide-react";

export default function Sidebar() {
  const navItems = [
    { name: "Overview / Home", to: "/", icon: Home },
    { name: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
    { name: "New Scan", to: "/new-scan", icon: Play },
    { name: "Findings & Memory", to: "/findings", icon: ShieldAlert },
    { name: "Reports", to: "/reports", icon: FileText },
    { name: "Security Telemetry", to: "/metrics", icon: BarChart3 }
  ];

  return (
    <aside className="w-[280px] min-h-screen bg-[#090D16] border-r border-[#1E293B] flex flex-col shrink-0">
      <div className="p-6 border-b border-[#1E293B] flex items-center justify-between">
        <Logo size="md" />
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition-all duration-200 group ${
                isActive
                  ? "bg-[#0284C7] text-white shadow-lg shadow-sky-500/20"
                  : "text-[#94A3B8] hover:bg-[#1E293B]/50 hover:text-[#F8FAFC]"
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-6 border-t border-[#1E293B] text-center text-xs text-[#64748B] font-mono">
        Phase 8 Active Mode
      </div>
    </aside>
  );
}
