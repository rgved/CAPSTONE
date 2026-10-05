import { NavLink } from "react-router-dom";
import Logo from "../brand/Logo";
import {
  LayoutDashboard,
  Play,
  ShieldAlert,
  FileText,
  BarChart3
} from "lucide-react";

export default function Sidebar() {
  const navItems = [
    { name: "Dashboard", to: "/", icon: LayoutDashboard },
    { name: "New Scan", to: "/new-scan", icon: Play },
    { name: "Findings", to: "/findings", icon: ShieldAlert },
    { name: "Reports", to: "/reports", icon: FileText },
    { name: "Metrics", to: "/metrics", icon: BarChart3 }
  ];

  return (
    <aside className="w-[280px] min-h-screen bg-[#111827] border-r border-[#1F2937] flex flex-col shrink-0">
      <div className="p-6 border-b border-[#1F2937] flex items-center justify-between">
        <Logo size="md" />
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? "bg-[#3B82F6] text-white shadow-lg shadow-blue-500/20"
                  : "text-[#94A3B8] hover:bg-[#1F2937] hover:text-[#F8FAFC]"
              }`
            }
          >
            <item.icon className="w-5 h-5 shrink-0" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-6 border-t border-[#1F2937] text-center text-xs text-[#94A3B8]">
        Phase 8 Active Mode
      </div>
    </aside>
  );
}
