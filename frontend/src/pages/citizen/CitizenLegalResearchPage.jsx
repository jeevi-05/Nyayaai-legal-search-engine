import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { searchCases } from "../../services/researchService";
import { Search, Scale, Building2, Calendar, Tag, AlertCircle, FileSearch, ArrowRight } from "lucide-react";

function ResultCard({ item, onOpen }) {
  const docId = item.doc_id || item.external_id;
  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h2 className="font-bold text-navy-600 text-sm leading-snug">{item.title}</h2>
          <div className="flex flex-wrap items-center gap-3 mt-2">
            {item.court && (
              <span className="flex items-center gap-1 text-xs text-gray-500"><Building2 size={11} />{item.court}</span>
            )}
            {item.year && (
              <span className="flex items-center gap-1 text-xs text-gray-500"><Calendar size={11} />{item.year}</span>
            )}
            {item.category && (
              <span className="flex items-center gap-1 text-xs text-gray-500"><Tag size={11} />{item.category}</span>
            )}
          </div>
        </div>
        <div className="w-9 h-9 bg-emerald-50 rounded-xl flex items-center justify-center shrink-0">
          <Scale size={16} className="text-emerald-600" />
        </div>
      </div>
      {item.description && (
        <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">{item.description}</p>
      )}
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

function SkeletonCard() {
  return (
    <div className="card p-5 space-y-3 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-100 rounded w-1/2" />
      <div className="h-3 bg-gray-100 rounded w-full" />
      <div className="h-3 bg-gray-100 rounded w-5/6" />
    </div>
  );
}

export default function CitizenLegalResearchPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setError("");
    setLoading(true);
    setSearched(true);
    try {
      const res = await searchCases(query);
      setResults(res.data.results || []);
    } catch {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-navy-600 rounded-3xl p-7 relative overflow-hidden">
        <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Search size={15} className="text-navy-300" />
            <span className="text-navy-300 text-xs font-semibold uppercase tracking-widest">Legal Research</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Search Legal Information</h1>
          <p className="text-navy-200 text-sm mt-1">Search cases, acts, and judgments using AI-powered semantic search</p>
        </div>
      </div>

      <div className="card p-5">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search size={17} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            <input
              className="input-field pl-11 py-3 text-base"
              placeholder="Search cases, acts, judgments... e.g. Article 21, consumer rights"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
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

      {error && (
        <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0" />{error}
        </div>
      )}

      {!loading && searched && results.length > 0 && (
        <p className="text-sm text-gray-500 font-medium">
          {results.length} result{results.length !== 1 ? "s" : ""} found for &ldquo;{query}&rdquo;
        </p>
      )}

      {loading && (
        <div className="space-y-4">{[1, 2, 3].map((i) => <SkeletonCard key={i} />)}</div>
      )}

      {!loading && results.length > 0 && (
        <div className="space-y-4">
          {results.map((item, i) => (
            <ResultCard key={item.id ?? i} item={item} onOpen={(id) => navigate(`/research/case/${id}`)} />
          ))}
        </div>
      )}

      {!loading && results.length === 0 && (
        <div className="text-center py-20 card">
          <div className="w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FileSearch size={28} className="text-emerald-400" />
          </div>
          <p className="font-semibold text-navy-600 mb-1">
            {searched ? "No results found" : "Search Indian legal documents"}
          </p>
          <p className="text-sm text-gray-400 max-w-xs mx-auto">
            {searched
              ? "Try different keywords or broaden your search terms."
              : "Enter a legal issue, case name, section, or keyword to find relevant laws and judgments."}
          </p>
        </div>
      )}
    </div>
  );
}
