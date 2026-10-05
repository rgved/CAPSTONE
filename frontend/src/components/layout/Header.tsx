import { useQuery } from "@tanstack/react-query";
import { api } from "../../services/api";
import { Shield, Target } from "lucide-react";

export default function Header() {
  const { data } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    refetchInterval: 5000 // Poll to keep live counts updated
  });

  const totalMissions = data?.stats?.total_missions ?? 0;
  const totalFindings = data?.stats?.total_findings ?? 0;

  return (
    <header className="h-16 border-b border-[#1F2937] bg-[#111827] flex items-center justify-between px-8 shrink-0">
      <div className="flex items-center gap-3">
        <span className="font-brand text-xl text-[#F8FAFC] italic tracking-tight">
          Sniff<span className="text-[#3B82F6]">.</span>
        </span>
        <span className="text-xs text-[#475569] font-mono">/</span>
        <h2 className="text-[#94A3B8] font-medium text-sm tracking-wide">
          Agentic Web Security Reconnaissance
        </h2>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#0B1220] border border-[#1F2937]">
          <Target className="w-4 h-4 text-[#3B82F6]" />
          <span className="text-xs text-[#94A3B8]">Missions:</span>
          <span className="text-xs font-bold text-[#F8FAFC]">{totalMissions}</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#0B1220] border border-[#1F2937]">
          <Shield className="w-4 h-4 text-[#EF4444]" />
          <span className="text-xs text-[#94A3B8]">Findings:</span>
          <span className="text-xs font-bold text-[#F8FAFC]">{totalFindings}</span>
        </div>
      </div>
    </header>
  );
}
