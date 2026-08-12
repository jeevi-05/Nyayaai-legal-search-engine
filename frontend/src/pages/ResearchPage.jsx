import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMode } from "../context/ModeContext";
import { searchCases } from "../services/researchService";
import {
  Search, Scale, Building2, Calendar, Tag,
  Brain, TrendingUp, AlertCircle, FileSearch, ArrowRight
} from "lucide-react";

const STRENGTH_CONFIG = {
  HIGH:   { color: "bg-emerald-100 text-emerald-700 border-emerald-200", bar: "bg-emerald-500", width: "w-full" },
  MEDIUM: { color: "bg-amber-100 text-amber-700 border-amber-200",       bar: "bg-amber-500",   width: "w-2/3"  },
  LOW:    { color: "bg-red-100 text-red-700 border-red-200",             bar: "bg-red-400",     width: "w-1/3"  },
};

function ResultCard({ caseItem, onOpen }) {
  const strength = caseItem.decision_support?.precedent_strength?.toUpperCase();
  const cfg = STRENGTH_CONFIG[strength] || STRENGTH_CONFIG.MEDIUM;
  const docId = caseItem.doc_id || caseItem.external_id;

  return (
    <div className="card p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h2 className="font-bold text-navy-600 text-base leading-snug">{caseItem.title}</h2>
          <div className="flex flex-wrap items-center gap-3 mt-2">
            {caseItem.court && (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                <Building2 size={12} /> {caseItem.court}
              </span>
            )}
            {caseItem.year && (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                <Calendar size={12} /> {caseItem.year}
              </span>
            )}
            {caseItem.category && (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                <Tag size={12} /> {caseItem.category}
              </span>
            )}
          </div>
        </div>
        <div className="w-10 h-10 bg-navy-50 rounded-xl flex items-center justify-center shrink-0">
          <Scale size={18} className="text-navy-600" />
        </div>
      </div>

      {/* Description */}
      {caseItem.description && (
        <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">{caseItem.description}</p>
      )}

      {/* Decision support */}
      {caseItem.decision_support && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Brain size={14} className="text-navy-600" />
            <span className="text-xs font-semibold text-navy-600 uppercase tracking-wide">AI Decision Support</span>
          </div>

          {caseItem.decision_support.recommendation && (
            <p className="text-sm text-gray-700 leading-relaxed">
              {caseItem.decision_support.recommendation}
            </p>
          )}

          {strength && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <TrendingUp size={13} className="text-gray-500" />
                <span className="text-xs text-gray-500 font-medium">Precedent Strength</span>
              </div>
              <span className={`badge border text-xs ${cfg.color}`}>{strength}</span>
              <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${cfg.bar} ${cfg.width}`} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* View detail button */}
      {docId && (
        <button
          onClick={() => onOpen(docId)}
          className="btn-primary w-full py-2.5 rounded-xl text-sm"
        >
          View Full Judgment <ArrowRight size={14} />
        </button>
      )}
    </div>
  );
}

function EmptyState({ searched, mode }) {
  return (
    <div className="text-center py-20 card">
      <div className="w-16 h-16 bg-navy-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <FileSearch size={28} className="text-navy-400" />
      </div>
      <p className="font-semibold text-navy-600 mb-1">
        {searched ? "No results found" : `Start your ${mode.name} research`}
      </p>
      <p className="text-sm text-gray-400 max-w-xs mx-auto">
        {searched
          ? "Try different keywords or broaden your search terms."
          : mode.id === 'citizen'
            ? "Enter a legal issue, case name, section, or keyword to find relevant laws."
            : mode.id === 'investigation'
              ? "Search criminal cases, legal provisions, and investigation-related documents."
              : "Enter a legal issue, case name, section, or keyword to search across Indian legal documents."
        }
      </p>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="card p-6 space-y-3 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-100 rounded w-1/2" />
      <div className="h-3 bg-gray-100 rounded w-full" />
      <div className="h-3 bg-gray-100 rounded w-5/6" />
      <div className="h-16 bg-slate-100 rounded-xl" />
    </div>
  );
}

export default function ResearchPage() {
  const { mode } = useMode();
  const navigate = useNavigate();
  const [query, setQuery]     = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const [searched, setSearched] = useState(false);

  const handleOpen = (docId) => navigate(`/research/case/${docId}`);

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setError("");
    setLoading(true);
    setSearched(true);
    try {
      const res = await searchCases(query);
      setResults(res.data.results || []);
    } catch (err) {
      setError("Search failed. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div className="space-y-6">

      {/* Page header */}
      <div className={`bg-${mode.color}-600 rounded-3xl p-7 relative overflow-hidden`}>
        <div className={`absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none`} />
        <div className={`absolute right-16 bottom-0 w-24 h-24 rounded-full bg-${mode.color}-400/10 pointer-events-none`} />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Search size={15} className={`text-${mode.color}-400`} />
            <span className={`text-${mode.color}-400 text-xs font-semibold uppercase tracking-widest`}>Legal Research</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Intelligent Case Search</h1>
          <p className={`text-${mode.color}-200 text-sm mt-1`}>
            Search Indian judgments, acts, sections and precedents using AI
          </p>
        </div>
      </div>

      {/* Search box */}
      <div className="card p-5">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search size={17} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            <input
              className="input-field pl-11 py-3 text-base"
              placeholder={mode.id === 'citizen'
                ? "Search for laws, cases, or legal information..."
                : mode.id === 'investigation'
                  ? "Search criminal cases, legal provisions..."
                  : "Search Indian judgments, acts, sections and precedents..."
              }
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary px-7 py-3 rounded-xl shrink-0"
          >
            {loading ? <span className="spinner" /> : <Search size={16} />}
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          {error}
        </div>
      )}

      {/* Results count */}
      {!loading && searched && results.length > 0 && (
        <p className="text-sm text-gray-500 font-medium">
          {results.length} result{results.length !== 1 ? "s" : ""} found for &ldquo;{query}&rdquo;
        </p>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {/* Results */}
      {!loading && results.length > 0 && (
        <div className="space-y-4">
          {results.map((caseItem, i) => (
            <ResultCard key={caseItem.id ?? i} caseItem={caseItem} onOpen={handleOpen} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && results.length === 0 && (
        <EmptyState searched={searched} mode={mode} />
      )}

    </div>
  );
}
