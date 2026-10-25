import { useQuery } from "@tanstack/react-query";
import { api } from "../../services/api";
import type { DashboardData } from "../../types";
import { Target, ShieldAlert, ShieldCheck, Layers } from "lucide-react";

interface SecurityMetricsStripProps {
  variant?: "full" | "compact";
  className?: string;
}

export default function SecurityMetricsStrip({ variant = "full", className = "" }: SecurityMetricsStripProps) {
  const { data } = useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    refetchInterval: 5000
  });

  const stats = data?.stats ?? {
    total_missions: 0,
    assets_scanned: 0,
    total_findings: 0,
    critical_findings: 0,
    high_findings: 0,
    security_score: 100,
    features_identified: 0
  };

  const securityScore = stats.security_score ?? (stats.total_findings === 0 ? 100 : Math.max(30, 100 - stats.total_findings * 12));
  const scoreColor = securityScore >= 80 ? "text-[#10B981]" : securityScore >= 60 ? "text-[#F59E0B]" : "text-[#EF4444]";
  const scoreBadge = securityScore >= 80 ? "Hardened" : securityScore >= 60 ? "Moderate" : "Elevated Risk";
  const scoreBadgeBg = securityScore >= 80 ? "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30" : securityScore >= 60 ? "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30" : "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30";

  if (variant === "compact") {
    return (
      <div className={`grid grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
        <div className="bg-[#0F172A] border border-[#1E293B] p-4 rounded-xl flex items-center justify-between shadow-sm hover:border-[#38BDF8]/40 transition-all">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Target Assets</span>
            <p className="text-xl font-bold text-[#F8FAFC] mt-1">{stats.assets_scanned || stats.total_missions}</p>
          </div>
          <div className="p-2.5 bg-[#38BDF8]/10 rounded-lg text-[#38BDF8] border border-[#38BDF8]/20">
            <Target className="w-4 h-4" />
          </div>
        </div>
        <div className="bg-[#0F172A] border border-[#1E293B] p-4 rounded-xl flex items-center justify-between shadow-sm hover:border-[#EF4444]/40 transition-all">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Active Findings</span>
            <p className="text-xl font-bold text-[#EF4444] mt-1">{stats.total_findings}</p>
          </div>
          <div className="p-2.5 bg-[#EF4444]/10 rounded-lg text-[#EF4444] border border-[#EF4444]/20">
            <ShieldAlert className="w-4 h-4" />
          </div>
        </div>
        <div className="bg-[#0F172A] border border-[#1E293B] p-4 rounded-xl flex items-center justify-between shadow-sm hover:border-[#10B981]/40 transition-all">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Defense Posture</span>
            <p className={`text-xl font-bold mt-1 ${scoreColor}`}>{securityScore} <span className="text-xs text-[#64748B]">/ 100</span></p>
          </div>
          <div className="p-2.5 bg-[#10B981]/10 rounded-lg text-[#10B981] border border-[#10B981]/20">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
        <div className="bg-[#0F172A] border border-[#1E293B] p-4 rounded-xl flex items-center justify-between shadow-sm hover:border-[#8B5CF6]/40 transition-all">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Capabilities</span>
            <p className="text-xl font-bold text-[#8B5CF6] mt-1">{stats.features_identified}</p>
          </div>
          <div className="p-2.5 bg-[#8B5CF6]/10 rounded-lg text-[#8B5CF6] border border-[#8B5CF6]/20">
            <Layers className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 ${className}`}>
      {/* Target Assets Scanned */}
      <div className="bg-[#0F172A] border border-[#1E293B] p-5 rounded-xl flex flex-col justify-between min-h-[136px] hover:border-[#38BDF8]/40 transition-all shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Target Assets</span>
            <div className="text-3xl font-extrabold text-[#F8FAFC] tracking-tight mt-1.5">{stats.assets_scanned || stats.total_missions}</div>
          </div>
          <div className="p-2.5 bg-[#38BDF8]/10 rounded-lg text-[#38BDF8] border border-[#38BDF8]/20 flex items-center justify-center shrink-0">
            <Target className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-[#1E293B]/60 flex items-center gap-1.5 text-xs text-[#94A3B8]">
          <span className="text-[#38BDF8] font-bold font-mono">{stats.total_missions}</span>
          <span>missions evaluated</span>
        </div>
      </div>

      {/* Security Findings */}
      <div className="bg-[#0F172A] border border-[#1E293B] p-5 rounded-xl flex flex-col justify-between min-h-[136px] hover:border-[#EF4444]/40 transition-all shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Active Findings</span>
            <div className="text-3xl font-extrabold text-[#F8FAFC] tracking-tight mt-1.5">{stats.total_findings}</div>
          </div>
          <div className="p-2.5 bg-[#EF4444]/10 rounded-lg text-[#EF4444] border border-[#EF4444]/20 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-[#1E293B]/60 flex items-center gap-1.5 text-xs">
          <span className="px-1.5 py-0.5 rounded bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/30 font-semibold font-mono text-[10px]">
            {stats.high_findings || 0} High / Critical
          </span>
          <span className="text-[#94A3B8]">requiring attention</span>
        </div>
      </div>

      {/* Defense Posture Score */}
      <div className="bg-[#0F172A] border border-[#1E293B] p-5 rounded-xl flex flex-col justify-between min-h-[136px] hover:border-[#10B981]/40 transition-all shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Defense Posture</span>
            <div className="flex items-baseline gap-1.5 mt-1.5">
              <span className={`text-3xl font-extrabold tracking-tight ${scoreColor}`}>{securityScore}</span>
              <span className="text-xs font-semibold text-[#64748B]">/ 100</span>
            </div>
          </div>
          <div className="p-2.5 bg-[#10B981]/10 rounded-lg text-[#10B981] border border-[#10B981]/20 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-[#1E293B]/60 flex items-center gap-1.5 text-xs">
          <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${scoreBadgeBg}`}>
            {scoreBadge}
          </span>
          <span className="text-[#94A3B8]">resilience rating</span>
        </div>
      </div>

      {/* Capabilities Mapped */}
      <div className="bg-[#0F172A] border border-[#1E293B] p-5 rounded-xl flex flex-col justify-between min-h-[136px] hover:border-[#8B5CF6]/40 transition-all shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider block">Surface Capabilities</span>
            <div className="text-3xl font-extrabold text-[#F8FAFC] tracking-tight mt-1.5">{stats.features_identified}</div>
          </div>
          <div className="p-2.5 bg-[#8B5CF6]/10 rounded-lg text-[#8B5CF6] border border-[#8B5CF6]/20 flex items-center justify-center shrink-0">
            <Layers className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-[#1E293B]/60 flex items-center gap-1.5 text-xs text-[#94A3B8]">
          <span className="text-[#A78BFA] font-bold">Functional areas</span>
          <span>mapped by workers</span>
        </div>
      </div>
    </div>
  );
}
