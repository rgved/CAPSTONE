import { useQuery } from "@tanstack/react-query";
import { api } from "../../services/api";
import { Shield, Target, LogOut, User as UserIcon } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Header() {
  const { user, isAuthenticated, openAuthModal, logout } = useAuth();
  const { data } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    refetchInterval: 5000 // Poll to keep live counts updated
  });

  const totalMissions = data?.stats?.total_missions ?? 0;
  const totalFindings = data?.stats?.total_findings ?? 0;

  return (
    <header className="h-16 border-b border-[#1E293B] bg-[#090D16] flex items-center justify-between px-8 shrink-0">
      <div className="flex items-center gap-3">
        <span className="font-brand text-xl text-[#F8FAFC] italic tracking-tight">
          Sniff<span className="text-[#38BDF8]">.</span>
        </span>
        <span className="text-xs text-[#64748B] font-mono">/</span>
        <h2 className="text-[#94A3B8] font-medium text-xs tracking-wide uppercase font-mono">
          Agentic Web Security Reconnaissance
        </h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0F172A] border border-[#1E293B] shadow-xs">
          <Target className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span className="text-xs text-[#64748B]">Missions:</span>
          <span className="text-xs font-bold text-[#F8FAFC] font-mono">{totalMissions}</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0F172A] border border-[#1E293B] shadow-xs">
          <Shield className="w-3.5 h-3.5 text-[#EF4444]" />
          <span className="text-xs text-[#64748B]">Findings:</span>
          <span className="text-xs font-bold text-[#F8FAFC] font-mono">{totalFindings}</span>
        </div>

        {/* User profile / auth action */}
        {isAuthenticated && user ? (
          <div className="flex items-center gap-2 pl-2 border-l border-[#1E293B]">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0F172A] border border-[#1E293B]">
              <div className="w-5 h-5 rounded-full bg-[#0284C7] text-white flex items-center justify-center text-[10px] font-bold font-mono">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <span className="text-xs font-mono text-[#E2E8F0]">@{user.username}</span>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-[#64748B] hover:text-[#EF4444] hover:bg-[#1E293B] transition cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => openAuthModal("login")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <UserIcon className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
}
