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
    <aside className="w-[280px] min-h-screen bg-[#0E1217] border-r-2 border-black flex flex-col shrink-0">
      <div className="p-6 border-b-2 border-black flex items-center justify-between">
        <Logo size="md" />
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-xs font-bold transition-all duration-150 group ${
                isActive
                  ? "bg-[#E2F952] text-black border-2 border-black shadow-[2.5px_2.5px_0px_#000] translate-x-0.5"
                  : "text-[#94A3B8] border-2 border-transparent hover:border-black hover:bg-[#141A23] hover:text-[#F8FAFC] hover:shadow-[2px_2px_0px_#000]"
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-6 border-t-2 border-black text-center text-xs text-[#94A3B8] font-mono font-bold bg-[#141A23]">
        <span className="font-editorial italic text-white mr-1.5">Sniff Engine</span>
        Phase 8 Mode
      </div>
    </aside>
  );
}
