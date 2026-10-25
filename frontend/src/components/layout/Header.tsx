import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../../services/api";
import { Shield, Target, LogOut, User as UserIcon } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Header() {
  const navigate = useNavigate();
  const { user, isAuthenticated, openAuthModal, logout } = useAuth();
  const { data } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    refetchInterval: 5000 // Poll to keep live counts updated
  });

  const totalMissions = data?.stats?.total_missions ?? 0;
  const totalFindings = data?.stats?.total_findings ?? 0;

  return (
    <header className="h-16 border-b-2 border-black bg-[#0E1217] flex items-center justify-between px-8 shrink-0">
      <div className="flex items-center gap-3">
        <span className="font-brand text-xl text-[#F8FAFC] italic tracking-tight">
          Sniff<span className="text-[#E2F952]">.</span>
        </span>
        <span className="text-xs text-[#475569] font-mono font-bold">/</span>
        <h2 className="text-[#94A3B8] font-semibold text-xs tracking-wider uppercase font-mono">
          Agentic Web Security Reconnaissance
        </h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000]">
          <Target className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span className="text-xs text-[#94A3B8] font-mono">Missions:</span>
          <span className="text-xs font-black text-[#F8FAFC] font-mono">{totalMissions}</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000]">
          <Shield className="w-3.5 h-3.5 text-[#EF4444]" />
          <span className="text-xs text-[#94A3B8] font-mono">Findings:</span>
          <span className="text-xs font-black text-[#F8FAFC] font-mono">{totalFindings}</span>
        </div>

        {/* User profile / auth action */}
        {isAuthenticated && user ? (
          <div className="flex items-center gap-2 pl-2 border-l border-[#202938]">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000]">
              <div className="w-5 h-5 rounded-md bg-[#E2F952] text-black border border-black flex items-center justify-center text-[10px] font-black font-mono">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <span className="text-xs font-mono text-[#E2E8F0] font-bold">@{user.username}</span>
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/");
              }}
              title="Sign Out"
              className="p-1.5 rounded-lg bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000] text-[#94A3B8] hover:text-black hover:bg-[#EF4444] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[3px_3px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 transition-all cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => openAuthModal("login")}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#E2F952] text-black text-xs font-black border-2 border-black shadow-[2px_2px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[3.5px_3.5px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 transition-all cursor-pointer"
          >
            <UserIcon className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
}
