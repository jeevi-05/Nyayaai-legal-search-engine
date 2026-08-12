import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { searchCases } from "../services/researchService";
import { useMode } from "../context/ModeContext";
import {
  Scale, Search, CheckCircle,
  AlertCircle, FileText, Brain,
  Info, Clock, Building2, Hash
} from "lucide-react";

const SIMILARITY_THRESHOLD = {
  HIGH: 0.85,
  MEDIUM: 0.70,
  LOW: 0.55
};

const SIMILARITY_CONFIG = {
  HIGH:   { color: "bg-emerald-100 text-emerald-700 border-emerald-200", bar: "bg-emerald-500", width: "w-full" },
  MEDIUM: { color: "bg-amber-100 text-amber-700 border-amber-200",       bar: "bg-amber-500",   width: "w-2/3"  },
  LOW:    { color: "bg-red-100 text-red-700 border-red-200",             bar: "bg-red-400",     width: "w-1/3"  },
};

function JudgmentSelector({ 
  label, 
  judgment, 
  onSelect, 
  onClear, 
  loading 
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      try {
        const res = await searchCases(searchQuery);
        setSearchResults(res.data.results || []);
        setShowResults(true);
      } catch (err) {
        console.error("Search failed:", err);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleSelect = (result) => {
    onSelect(result);
    setSearchQuery("");
    setShowResults(false);
  };

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-navy-600">{label}</h3>
        {judgment && (
          <button
            onClick={onClear}
            className="text-xs text-red-600 hover:text-red-700 font-medium"
          >
            Clear
          </button>
        )}
      </div>

      {!judgment ? (
        <div className="relative">
          <Search 
            size={17} 
            className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" 
          />
          <input
            className="input-field pl-11 py-3 text-base"
            placeholder={`Search ${label}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchQuery && setShowResults(true)}
          />
          
          {showResults && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-gray-200 z-50 max-h-80 overflow-y-auto">
              {searchResults.map((result, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(result)}
                  className="w-full text-left px-4 py-3 hover:bg-navy-50 transition-colors border-b border-gray-100 last:border-0"
                >
                  <p className="font-medium text-navy-700 text-sm">{result.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {result.court && (
                      <span className="flex items-center gap-1 text-xs text-gray-500">
                        <Building2 size={10} /> {result.court}
                      </span>
                    )}
                    {result.year && (
                      <span className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock size={10} /> {result.year}
                      </span>
                    )}
                    <span className="text-xs text-gray-400">
                      {result.similarity || 0}% match
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="bg-navy-50 rounded-xl p-4 border border-navy-100">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold text-navy-700 text-sm">{judgment.title}</p>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                {judgment.court && (
                  <span className="flex items-center gap-1 text-xs text-gray-600 bg-white px-2 py-1 rounded-lg">
                    <Building2 size={10} /> {judgment.court}
                  </span>
                )}
                {judgment.year && (
                  <span className="flex items-center gap-1 text-xs text-gray-600 bg-white px-2 py-1 rounded-lg">
                    <Clock size={10} /> {judgment.year}
                  </span>
                )}
                {judgment.citation && (
                  <span className="flex items-center gap-1 text-xs text-gray-600 bg-white px-2 py-1 rounded-lg">
                    <Hash size={10} /> {judgment.citation}
                  </span>
                )}
              </div>
            </div>
            <CheckCircle size={16} className="text-emerald-500" />
          </div>
        </div>
      )}
    </div>
  );
}

function SimilarityBar({ score, label }) {
  const config = score >= SIMILARITY_THRESHOLD.HIGH * 100 
    ? SIMILARITY_CONFIG.HIGH 
    : score >= SIMILARITY_THRESHOLD.MEDIUM * 100 
      ? SIMILARITY_CONFIG.MEDIUM 
      : SIMILARITY_CONFIG.LOW;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-600">{label}</span>
        <span className={`text-xs font-bold ${config.color.split(" ")[1]}`}>{score}%</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full ${config.bar}`} 
          style={{ width: `${score}%` }} 
        />
      </div>
    </div>
  );
}

export default function JudgmentComparisonPage() {
  const { mode } = useMode();
  const navigate = useNavigate();
  
  // State hooks - must be at top level (before any early returns)
  const [judgmentA, setJudgmentA] = useState(null);
  const [judgmentB, setJudgmentB] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  
  // Only allow access in Judicial Intelligence Mode
  if (mode.id !== 'judicial') {
    return (
      <div className="max-w-2xl mx-auto py-20">
        <div className="card p-8 text-center">
          <div className="w-16 h-16 bg-amber-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Scale size={32} className="text-amber-500" />
          </div>
          <h2 className="text-xl font-bold text-navy-600 mb-2">Feature Restricted</h2>
          <p className="text-gray-600 mb-6">
            Judgment Comparison is available only in Judicial Intelligence Mode.
            Please switch modes to access this feature.
          </p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="btn-outline px-6 py-2.5 rounded-xl"
            >
              Go Back
            </button>
            <button
              onClick={() => navigate("/select-mode")}
              className="btn-primary px-6 py-2.5 rounded-xl"
            >
              Switch Mode
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleCompare = async () => {
    if (!judgmentA || !judgmentB) {
      setError("Please select both judgments to compare.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/judgments/compare", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mode: mode.id,
          judgment_a_id: judgmentA.doc_id || judgmentA.id,
          judgment_b_id: judgmentB.doc_id || judgmentB.id
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || "Comparison failed");
      }

      setComparison(data.data);
    } catch (err) {
      setError(err.message || "Comparison failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getSimilarityColor = (score) => {
    if (score >= SIMILARITY_THRESHOLD.HIGH * 100) return "text-emerald-600";
    if (score >= SIMILARITY_THRESHOLD.MEDIUM * 100) return "text-amber-600";
    return "text-red-600";
  };

  const getSimilarityBadge = (score) => {
    if (score >= SIMILARITY_THRESHOLD.HIGH * 100) return "High";
    if (score >= SIMILARITY_THRESHOLD.MEDIUM * 100) return "Moderate";
    return "Low";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`bg-${mode.color}-600 rounded-3xl p-7 relative overflow-hidden`}>
        <div className={`absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none`} />
        <div className={`absolute right-16 bottom-0 w-24 h-24 rounded-full bg-${mode.color}-400/10 pointer-events-none`} />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Scale size={15} className={`text-${mode.color}-400`} />
            <span className={`text-${mode.color}-400 text-xs font-semibold uppercase tracking-widest`}>Judgment Comparison</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Compare Two Legal Judgments</h1>
          <p className={`text-${mode.color}-200 text-sm mt-1`}>
            Semantic comparison of legal judgments using AI embeddings
          </p>
        </div>
      </div>

      {/* Selection Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <JudgmentSelector
          label="Judgment A"
          judgment={judgmentA}
          onSelect={setJudgmentA}
          onClear={() => setJudgmentA(null)}
        />
        <JudgmentSelector
          label="Judgment B"
          judgment={judgmentB}
          onSelect={setJudgmentB}
          onClear={() => setJudgmentB(null)}
        />
      </div>

      {/* Compare Button */}
<div className="flex justify-center">
  <button
    onClick={handleCompare}
    disabled={!judgmentA || !judgmentB || loading}
    className={`
      btn-primary px-8 py-3 rounded-xl text-base font-semibold
      disabled:opacity-50 disabled:cursor-not-allowed
      flex items-center gap-2
    `}
  >
    {loading ? (
      <>
        <span className="spinner" /> Comparing...
      </>
    ) : (
      <>
        <Scale size={18} /> Compare Judgments
      </>
    )}
  </button>
</div>
     {/* Error */}
      {error && (
        <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          {error}
        </div>
      )}

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-6">
          {/* Overall Similarity */}
          <div className={`bg-${mode.color}-50 border border-${mode.color}-200 rounded-2xl p-6`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-semibold text-${mode.color}-600 uppercase tracking-widest mb-1`}>
                  Overall Semantic Similarity
                </p>
                <div className="flex items-baseline gap-2">
                  <span className={`text-5xl font-bold ${getSimilarityColor(comparison.overall_similarity)}`}>
                    {comparison.overall_similarity}%
                  </span>
                  <span className={`text-sm font-medium ${getSimilarityColor(comparison.overall_similarity)}`}>
                    ({getSimilarityBadge(comparison.overall_similarity)} match)
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 mb-2">Based on semantic embeddings</p>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Info size={12} />
                  <span>{comparison.chunk_count_a} chunks vs {comparison.chunk_count_b} chunks</span>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex flex-wrap gap-2 border-b border-gray-200">
            {[
              { id: "overview", label: "Overview" },
              { id: "facts", label: "Facts" },
              { id: "issues", label: "Legal Issues" },
              { id: "arguments", label: "Arguments" },
              { id: "statutes", label: "Statutes" },
              { id: "precedents", label: "Precedents" },
              { id: "reasoning", label: "Reasoning" },
              { id: "outcome", label: "Outcome" },
              { id: "matches", label: "Detailed Matches" }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  px-4 py-2.5 rounded-t-lg text-sm font-medium transition-colors
                  ${activeTab === tab.id
                    ? `bg-white border-t-2 border-${mode.color}-500 text-${mode.color}-600`
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-b-xl border border-t-0 border-gray-200 p-6 min-h-[400px]">
            {activeTab === "overview" && (
              <div className="space-y-6">
                {/* Judgment Metadata */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                    <h3 className="font-semibold text-navy-600 mb-4 flex items-center gap-2">
                      <FileText size={16} /> Judgment A
                    </h3>
                    <p className="font-medium text-navy-700 mb-2">{comparison.judgment_a.case_title}</p>
                    <div className="space-y-1 text-sm text-gray-600">
                      {comparison.judgment_a.court && (
                        <p className="flex items-center gap-2">
                          <Building2 size={14} /> {comparison.judgment_a.court}
                        </p>
                      )}
                      {comparison.judgment_a.year && (
                        <p className="flex items-center gap-2">
                          <Clock size={14} /> {comparison.judgment_a.year}
                        </p>
                      )}
                      {comparison.judgment_a.citation && (
                        <p className="flex items-center gap-2">
                          <Hash size={14} /> {comparison.judgment_a.citation}
                        </p>
                      )}
                      {comparison.judgment_a.bench && (
                        <p className="flex items-center gap-2">
                          <Scale size={14} /> {comparison.judgment_a.bench}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                    <h3 className="font-semibold text-navy-600 mb-4 flex items-center gap-2">
                      <FileText size={16} /> Judgment B
                    </h3>
                    <p className="font-medium text-navy-700 mb-2">{comparison.judgment_b.case_title}</p>
                    <div className="space-y-1 text-sm text-gray-600">
                      {comparison.judgment_b.court && (
                        <p className="flex items-center gap-2">
                          <Building2 size={14} /> {comparison.judgment_b.court}
                        </p>
                      )}
                      {comparison.judgment_b.year && (
                        <p className="flex items-center gap-2">
                          <Clock size={14} /> {comparison.judgment_b.year}
                        </p>
                      )}
                      {comparison.judgment_b.citation && (
                        <p className="flex items-center gap-2">
                          <Hash size={14} /> {comparison.judgment_b.citation}
                        </p>
                      )}
                      {comparison.judgment_b.bench && (
                        <p className="flex items-center gap-2">
                          <Scale size={14} /> {comparison.judgment_b.bench}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Key Similarities */}
                {comparison.comparison && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-navy-600">Key Similarities</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[
                        { label: "Facts", score: comparison.comparison.facts.similarity_score },
                        { label: "Legal Issues", score: comparison.comparison.legal_issues.similarity_score },
                        { label: "Arguments", score: comparison.comparison.arguments.similarity_score },
                        { label: "Statutes", score: comparison.comparison.statutes.similarity_score },
                        { label: "Precedents", score: comparison.comparison.precedents.similarity_score },
                        { label: "Reasoning", score: comparison.comparison.reasoning.similarity_score },
                        { label: "Outcome", score: comparison.comparison.outcome.similarity_score }
                      ].map((item, idx) => (
                        <div key={idx} className="bg-slate-50 rounded-lg p-3">
                          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">{item.label}</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className={`h-full rounded-full ${item.score >= 70 ? "bg-emerald-500" : item.score >= 50 ? "bg-amber-500" : "bg-red-400"}`}
                                style={{ width: `${item.score}%` }}
                              />
                            </div>
                            <span className="text-xs font-bold text-gray-700">{item.score}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === "facts" && comparison.comparison?.facts && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment A</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.facts.judgment_a}</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment B</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.facts.judgment_b}</p>
                  </div>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <h4 className="font-semibold text-amber-700 mb-2 flex items-center gap-2">
                    <Info size={16} /> Similarity Analysis
                  </h4>
                  <p className="text-sm text-amber-800">
                    Similarity Score: {comparison.comparison.facts.similarity_score}%
                    {comparison.comparison.facts.common_elements && comparison.comparison.facts.common_elements.length > 0 && (
                      <span className="block mt-2">
                        Common elements: {comparison.comparison.facts.common_elements.join(", ")}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            )}

            {activeTab === "issues" && comparison.comparison?.legal_issues && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment A</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.legal_issues.judgment_a}</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment B</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.legal_issues.judgment_b}</p>
                  </div>
                </div>
                {comparison.comparison.legal_issues.common_issues && (
                  <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                    <h4 className="font-semibold text-emerald-700 mb-2">Common Legal Issues</h4>
                    <p className="text-sm text-emerald-800">{comparison.comparison.legal_issues.common_issues}</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === "arguments" && comparison.comparison?.arguments && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment A</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.arguments.judgment_a}</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment B</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.arguments.judgment_b}</p>
                  </div>
                </div>
                <SimilarityBar 
                  score={comparison.comparison.arguments.similarity_score} 
                  label="Argument Similarity" 
                />
              </div>
            )}

            {activeTab === "statutes" && comparison.comparison?.statutes && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Common Statutes</h4>
                    {comparison.comparison.statutes.common_statutes.length > 0 ? (
                      <ul className="space-y-1">
                        {comparison.comparison.statutes.common_statutes.map((statute, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                            <CheckCircle size={14} className="text-emerald-500" />
                            {statute}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">No common statutes found</p>
                    )}
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Only in Judgment A</h4>
                    {comparison.comparison.statutes.only_in_judgment_a.length > 0 ? (
                      <ul className="space-y-1">
                        {comparison.comparison.statutes.only_in_judgment_a.map((statute, idx) => (
                          <li key={idx} className="text-sm text-gray-700">{statute}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">None</p>
                    )}
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Only in Judgment B</h4>
                    {comparison.comparison.statutes.only_in_judgment_b.length > 0 ? (
                      <ul className="space-y-1">
                        {comparison.comparison.statutes.only_in_judgment_b.map((statute, idx) => (
                          <li key={idx} className="text-sm text-gray-700">{statute}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">None</p>
                    )}
                  </div>
                </div>
                <SimilarityBar 
                  score={comparison.comparison.statutes.similarity_score} 
                  label="Statute Similarity" 
                />
              </div>
            )}

            {activeTab === "precedents" && comparison.comparison?.precedents && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Common Precedents</h4>
                    {comparison.comparison.precedents.common_precedents.length > 0 ? (
                      <ul className="space-y-1">
                        {comparison.comparison.precedents.common_precedents.map((prec, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                            <CheckCircle size={14} className="text-emerald-500" />
                            {prec}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">No common precedents found</p>
                    )}
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Only in Judgment A</h4>
                    {comparison.comparison.precedents.only_in_judgment_a.length > 0 ? (
                      <ul className="space-y-1">
                        {comparison.comparison.precedents.only_in_judgment_a.map((prec, idx) => (
                          <li key={idx} className="text-sm text-gray-700">{prec}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">None</p>
                    )}
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Only in Judgment B</h4>
                    {comparison.comparison.precedents.only_in_judgment_b.length > 0 ? (
                      <ul className="space-y-1">
                        {comparison.comparison.precedents.only_in_judgment_b.map((prec, idx) => (
                          <li key={idx} className="text-sm text-gray-700">{prec}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">None</p>
                    )}
                  </div>
                </div>
                <SimilarityBar 
                  score={comparison.comparison.precedents.similarity_score} 
                  label="Precedent Similarity" 
                />
              </div>
            )}

            {activeTab === "reasoning" && comparison.comparison?.reasoning && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment A Reasoning</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.reasoning.judgment_a}</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment B Reasoning</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.reasoning.judgment_b}</p>
                  </div>
                </div>
                <div className={`p-4 rounded-xl border ${
                  comparison.comparison.reasoning.relationship.includes("Similar")
                    ? "bg-emerald-50 border-emerald-200"
                    : comparison.comparison.reasoning.relationship.includes("Different")
                      ? "bg-amber-50 border-amber-200"
                      : "bg-red-50 border-red-200"
                }`}>
                  <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <Brain size={16} /> Legal Approach
                  </h4>
                  <p className="text-sm text-gray-800">
                    {comparison.comparison.reasoning.relationship}
                  </p>
                </div>
                <SimilarityBar 
                  score={comparison.comparison.reasoning.similarity_score} 
                  label="Reasoning Similarity" 
                />
              </div>
            )}

            {activeTab === "outcome" && comparison.comparison?.outcome && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment A Outcome</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.outcome.judgment_a}</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <h4 className="font-semibold text-navy-600 mb-2">Judgment B Outcome</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{comparison.comparison.outcome.judgment_b}</p>
                  </div>
                </div>
                <SimilarityBar 
                  score={comparison.comparison.outcome.similarity_score} 
                  label="Outcome Similarity" 
                />
              </div>
            )}

            {activeTab === "matches" && comparison.semantic_matches && (
              <div className="space-y-4">
                <h3 className="font-semibold text-navy-600">Semantic Matches</h3>
                {comparison.semantic_matches.length > 0 ? (
                  <div className="space-y-3">
                    {comparison.semantic_matches.slice(0, 10).map((match, idx) => (
                      <div key={idx} className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                            Semantic Similarity: {match.similarity}%
                          </span>
                          {match.threshold_passed && (
                            <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">
                              Strong Match
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <div className="bg-white rounded-lg p-3 border border-gray-200">
                            <p className="text-xs text-gray-500 mb-1">Judgment A</p>
                            <p className="text-sm text-gray-700 line-clamp-3">{match.chunk_a.text}</p>
                          </div>
                          <div className="bg-white rounded-lg p-3 border border-gray-200">
                            <p className="text-xs text-gray-500 mb-1">Judgment B</p>
                            <p className="text-sm text-gray-700 line-clamp-3">{match.chunk_b.text}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No significant semantic matches found.</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
