import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import SecurityMetricsStrip from "../components/common/SecurityMetricsStrip";
import {
  Database,
  Search,
  BrainCircuit,
  Sparkles,
  ShieldAlert,
  Layers,
  Compass,
  Cpu,
  RefreshCw,
  Zap
} from "lucide-react";

export default function SemanticMemory() {
  const [searchQuery, setSearchQuery] = useState("");
  const [collection, setCollection] = useState("findings");
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [searching, setSearching] = useState(false);

  const { data: memorySummary, isLoading, refetch } = useQuery({
    queryKey: ["memory-summary"],
    queryFn: api.getMemorySummary,
    refetchInterval: 10000,
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      setSearching(true);
      const res = await api.searchMemory(searchQuery, collection);
      setSearchResults(res.results || []);
    } catch (err) {
      console.error("Semantic search failed", err);
    } finally {
      setSearching(false);
    }
  };

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "bg-[#DC2626] text-black border border-black shadow-[1.5px_1.5px_0px_#000000]";
      case "high":
        return "bg-[#EF4444] text-white border border-black shadow-[1.5px_1.5px_0px_#000000]";
      case "medium":
        return "bg-[#F59E0B] text-black border border-black shadow-[1.5px_1.5px_0px_#000000]";
      case "low":
        return "bg-[#10B981] text-black border border-black shadow-[1.5px_1.5px_0px_#000000]";
      default:
        return "bg-[#CBD5E1] text-black border border-black shadow-[1.5px_1.5px_0px_#000000]";
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner / Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b-2 border-black pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-[#F8FAFC] tracking-tight">
              <span>ChromaDB </span>
              <span className="font-editorial italic font-normal text-[#E2F952]">Semantic Memory</span>
            </h1>
            <span className="px-2.5 py-0.5 rounded text-[10px] font-black uppercase bg-[#E2F952] text-black border-2 border-black shadow-[2px_2px_0px_#000000] flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-black" /> Vector RAG Store
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1.5 leading-relaxed">
            Persistent embedding store that indexes prior observations to improve subsequent reconnaissance and vulnerability reasoning.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-[#141A23] hover:bg-[#1E293B] border-2 border-black rounded shadow-[2px_2px_0px_#000000] text-xs font-bold text-[#F8FAFC] transition-transform active:translate-x-0.5 active:translate-y-0.5 self-start md:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5 text-[#E2F952]" /> Refresh Store
        </button>
      </div>

      {/* Unified Platform Metrics Strip */}
      <SecurityMetricsStrip variant="full" />

      {/* Vector Collection Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#141A23] border-2 border-black p-6 rounded shadow-[4px_4px_0px_#000000] relative overflow-hidden transition-transform hover:-translate-y-0.5">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-black text-[#94A3B8] uppercase tracking-wider">Findings Collection</p>
              <h3 className="text-3xl font-black font-mono text-[#F8FAFC] mt-2">
                {isLoading ? "..." : memorySummary?.counts?.findings_indexed ?? 0}
              </h3>
            </div>
            <div className="p-3 bg-[#EF4444] text-white border-2 border-black rounded shadow-[2px_2px_0px_#000000]">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-[#94A3B8] font-mono">
            <span>Indexed vulnerability reasoning & evidence vectors</span>
          </div>
        </div>

        <div className="bg-[#141A23] border-2 border-black p-6 rounded shadow-[4px_4px_0px_#000000] relative overflow-hidden transition-transform hover:-translate-y-0.5">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-black text-[#94A3B8] uppercase tracking-wider">Features Collection</p>
              <h3 className="text-3xl font-black font-mono text-[#F8FAFC] mt-2">
                {isLoading ? "..." : memorySummary?.counts?.features_indexed ?? 0}
              </h3>
            </div>
            <div className="p-3 bg-[#E2F952] text-black border-2 border-black rounded shadow-[2px_2px_0px_#000000]">
              <Layers className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-[#94A3B8] font-mono">
            <span>Semantic capability fingerprints & route patterns</span>
          </div>
        </div>

        <div className="bg-[#141A23] border-2 border-black p-6 rounded shadow-[4px_4px_0px_#000000] relative overflow-hidden transition-transform hover:-translate-y-0.5">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-black text-[#94A3B8] uppercase tracking-wider">Routes Collection</p>
              <h3 className="text-3xl font-black font-mono text-[#F8FAFC] mt-2">
                {isLoading ? "..." : memorySummary?.counts?.routes_indexed ?? 0}
              </h3>
            </div>
            <div className="p-3 bg-[#10B981] text-black border-2 border-black rounded shadow-[2px_2px_0px_#000000]">
              <Compass className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-[#94A3B8] font-mono">
            <span>Discovered URL endpoints & structural DOM summaries</span>
          </div>
        </div>
      </div>

      {/* How Future Missions Use Semantic Memory */}
      <div className="bg-[#141A23] border-2 border-black rounded p-6 lg:p-8 space-y-6 shadow-[4px_4px_0px_#000000]">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-[#E2F952] text-black border-2 border-black rounded shadow-[2px_2px_0px_#000000]">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-black text-[#F8FAFC]">
              <span>How Future Missions Use </span>
              <span className="font-editorial italic font-normal text-[#E2F952]">Semantic Memory</span>
            </h2>
            <p className="text-xs text-[#94A3B8]">Cross-mission memory transfers knowledge so each scan is smarter than the last.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000000] space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#E2F952]">
              <Compass className="w-4 h-4" /> 1. Capability Matching
            </div>
            <p className="text-xs text-[#CBD5E1] leading-relaxed">
              When encountering an ambiguous endpoint, the feature extractor queries ChromaDB vectors to find which capabilities similar pages mapped to in previous targets.
            </p>
          </div>

          <div className="p-4 rounded bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000000] space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#E2F952]">
              <Cpu className="w-4 h-4" /> 2. Few-Shot In-Context Injection
            </div>
            <p className="text-xs text-[#CBD5E1] leading-relaxed">
              During <code className="text-[#E2F952] bg-black px-1.5 py-0.5 rounded font-mono text-[11px] border border-black">RUN_ANALYSIS</code>, the orchestrator retrieves the 3 closest past findings and supplies them to Groq LLM as historical evidence context.
            </p>
          </div>

          <div className="p-4 rounded bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000000] space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#10B981]">
              <Zap className="w-4 h-4" /> 3. High-Yield Crawl Elevation
            </div>
            <p className="text-xs text-[#CBD5E1] leading-relaxed">
              The risk scorer boosts parameters and routes that share vector patterns with previously confirmed vulnerabilities, guiding the crawler toward fertile attack surfaces.
            </p>
          </div>
        </div>
      </div>
      {/* Interactive Semantic Search Bar */}
      <div className="bg-[#141A23] border-2 border-black rounded p-6 lg:p-8 space-y-6 shadow-[4px_4px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-2 border-black pb-4">
          <div>
            <h2 className="text-base font-black text-[#F8FAFC] flex items-center gap-2">
              <Search className="w-4 h-4 text-[#E2F952]" /> <span>Query </span><span className="font-editorial italic font-normal text-[#E2F952]">Vector Index</span>
            </h2>
            <p className="text-xs text-[#94A3B8]">Test semantic similarity search across vector collections in real-time.</p>
          </div>

          {/* Collection Filter */}
          <div className="flex bg-[#0E1217] p-1 rounded border-2 border-black shadow-[2px_2px_0px_#000000] self-start sm:self-auto gap-1">
            {["findings", "features", "routes"].map((col) => (
              <button
                key={col}
                type="button"
                onClick={() => {
                  setCollection(col);
                  setSearchResults(null);
                }}
                className={`px-3 py-1 text-xs font-bold rounded capitalize transition-all border ${
                  collection === col
                    ? "bg-[#E2F952] text-black border-black shadow-[1px_1px_0px_#000000]"
                    : "text-[#94A3B8] border-transparent hover:text-[#F8FAFC]"
                }`}
              >
                {col}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#94A3B8] absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={`Search ${collection} by meaning (e.g. "missing csrf token", "admin authentication", "file extension validation")...`}
              className="w-full bg-[#0E1217] border-2 border-black rounded pl-11 pr-4 py-3 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#E2F952] shadow-[2px_2px_0px_#000000] outline-none transition-all font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="px-6 py-3 bg-[#E2F952] hover:bg-[#D4EB3E] text-black font-extrabold text-xs rounded border-2 border-black shadow-[3px_3px_0px_#000000] hover:shadow-[1px_1px_0px_#000000] hover:translate-x-[2px] hover:translate-y-[2px] disabled:opacity-50 transition-all flex items-center gap-2 shrink-0 cursor-pointer"
          >
            {searching ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Vector Search
          </button>
        </form>

        {/* Live Search Results */}
        {searchResults !== null && (
          <div className="space-y-3 pt-4 border-t-2 border-black">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold text-[#94A3B8]">
                Matched {searchResults.length} {searchResults.length === 1 ? "document" : "documents"} for "{searchQuery}"
              </span>
              <button
                type="button"
                onClick={() => setSearchResults(null)}
                className="text-xs font-bold text-[#E2F952] hover:underline"
              >
                Clear Results
              </button>
            </div>

            {searchResults.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#94A3B8] bg-[#0E1217] rounded border-2 border-black shadow-[2px_2px_0px_#000000]">
                No vector matches found with current query threshold.
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {searchResults.map((res, i) => (
                  <div
                    key={i}
                    className="p-4 rounded bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000000] space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-black text-[#F8FAFC] bg-black px-2 py-0.5 rounded border border-black">
                          {res.document_id}
                        </span>
                        {res.metadata?.severity && (
                          <span
                            className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${getSeverityBadgeClass(
                              res.metadata.severity
                            )}`}
                          >
                            {res.metadata.severity}
                          </span>
                        )}
                        {res.metadata?.feature && (
                          <span className="text-[10px] font-mono text-[#CBD5E1] bg-[#141A23] px-2 py-0.5 rounded border border-black">
                            {res.metadata.feature}
                          </span>
                        )}
                      </div>
                      <span className="text-xs font-mono font-black text-black bg-[#E2F952] px-2 py-0.5 rounded border border-black shadow-[1px_1px_0px_#000000]">
                        {res.similarity_score}% Match
                      </span>
                    </div>
                    <p className="text-xs font-mono text-[#CBD5E1] whitespace-pre-wrap leading-relaxed line-clamp-3">
                      {res.document}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stored Historical Findings Preview */}
      <div className="bg-[#141A23] border-2 border-black rounded p-6 lg:p-8 space-y-6 shadow-[4px_4px_0px_#000000]">
        <div className="border-b-2 border-black pb-4">
          <h2 className="text-base font-black text-[#F8FAFC] flex items-center gap-2">
            <Database className="w-4 h-4 text-[#E2F952]" /> <span>Stored </span><span className="font-editorial italic font-normal text-[#E2F952]">Semantic Knowledge Base</span>
          </h2>
          <p className="text-xs text-[#94A3B8]">Observations currently embedded and available to subsequent analysis workflows.</p>
        </div>

        {memorySummary?.recent_stored_findings?.length === 0 ? (
          <div className="p-8 text-center text-xs text-[#94A3B8] bg-[#0E1217] rounded border-2 border-black shadow-[2px_2px_0px_#000000]">
            No findings indexed yet. Run your first mission to populate semantic memory!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b-2 border-black text-[#94A3B8] uppercase tracking-wider font-bold">
                  <th className="pb-3">ID</th>
                  <th className="pb-3">Title</th>
                  <th className="pb-3">Category</th>
                  <th className="pb-3">Feature Context</th>
                  <th className="pb-3">Severity</th>
                  <th className="pb-3">Embedded Excerpt</th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-black">
                {memorySummary?.recent_stored_findings?.map((f: any, idx: number) => (
                  <tr key={idx} className="hover:bg-[#0E1217] transition-colors">
                    <td className="py-3 font-mono text-[#E2F952] font-black">{f.id}</td>
                    <td className="py-3 font-bold text-[#F8FAFC] max-w-[200px] truncate" title={f.title}>
                      {f.title}
                    </td>
                    <td className="py-3 text-[#CBD5E1] font-mono text-[11px]">{f.type}</td>
                    <td className="py-3 text-[#CBD5E1] font-mono text-[11px]">{f.feature}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${getSeverityBadgeClass(f.severity)}`}>
                        {f.severity}
                      </span>
                    </td>
                    <td className="py-3 text-[#94A3B8] max-w-[320px] truncate font-mono text-[11px]" title={f.snippet}>
                      {f.snippet}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
