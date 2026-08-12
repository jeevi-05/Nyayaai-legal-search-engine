import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getCaseDetail, addCaseToRepository } from "../services/researchService";
import api from "../api/axios";
import {
  ArrowLeft, Download, BookPlus, Search, Scale, Building2,
  Calendar, Hash, User, FileText, AlertCircle, CheckCircle,
  Brain, TrendingUp, Gavel, BookOpen, Lightbulb, ChevronDown,
  ChevronUp, ExternalLink, Tag, Loader,
} from "lucide-react";

const STRENGTH = {
  HIGH:   { cls: "bg-emerald-100 text-emerald-700 border-emerald-200", bar: "bg-emerald-500", w: "w-full" },
  MEDIUM: { cls: "bg-amber-100 text-amber-700 border-amber-200",       bar: "bg-amber-500",   w: "w-2/3"  },
  LOW:    { cls: "bg-red-100 text-red-700 border-red-200",             bar: "bg-red-400",     w: "w-1/3"  },
};

function Section({ icon: Icon, title, children, defaultOpen = true, accent = false, hasContent = true }) {
  const [open, setOpen] = useState(defaultOpen);
  if (!hasContent) return null;
  return (
    <div className={`card overflow-hidden ${accent ? "border-gold-400/40" : ""}`}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-navy-50 rounded-lg flex items-center justify-center">
            <Icon size={15} className="text-navy-600" />
          </div>
          <span className="font-semibold text-navy-600 text-sm">{title}</span>
        </div>
        {open ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
      </button>
      {open && <div className="px-6 pb-6 pt-1">{children}</div>}
    </div>
  );
}

function TextBlock({ text }) {
  if (!text?.trim()) return null;
  return <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{text}</p>;
}

function ActsChips({ value }) {
  if (!value?.trim()) return null;
  const items = [...new Set(value.split(",").map((s) => s.trim()).filter(Boolean))];
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span key={item} className="flex items-center gap-1 text-xs bg-navy-50 text-navy-700 border border-navy-100 px-2.5 py-1 rounded-lg font-medium">
          <Tag size={10} /> {item}
        </span>
      ))}
    </div>
  );
}

function SimilarCard({ item, onOpen }) {
  const pct   = Math.round(item.similarity ?? 0);
  const color = pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-red-400";
  const badge = pct >= 75 ? "bg-emerald-100 text-emerald-700" : pct >= 50 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700";
  const id    = item.external_id || item.doc_id;
  return (
    <div className="card p-4 space-y-2 hover:border-gold-400 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold text-navy-600 leading-snug line-clamp-2">{item.title}</p>
        <span className={`badge text-[10px] shrink-0 ${badge}`}>{pct}%</span>
      </div>
      {item.court && (
        <p className="text-xs text-gray-400 flex items-center gap-1">
          <Building2 size={10} /> {item.court}
        </p>
      )}
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      {id && (
        <button
          onClick={() => onOpen(id)}
          className="text-xs text-navy-600 font-semibold hover:text-gold-500 transition-colors flex items-center gap-1 mt-1"
        >
          View Case <ArrowLeft size={10} className="rotate-180" />
        </button>
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="space-y-5 animate-pulse">
      <div className="card p-7 space-y-4">
        <div className="h-6 bg-gray-200 rounded w-3/4" />
        <div className="flex gap-3">
          <div className="h-5 bg-gray-100 rounded w-32" />
          <div className="h-5 bg-gray-100 rounded w-20" />
          <div className="h-5 bg-gray-100 rounded w-24" />
        </div>
        <div className="flex gap-2 pt-2">
          <div className="h-9 bg-gray-200 rounded-xl w-36" />
          <div className="h-9 bg-gray-200 rounded-xl w-40" />
          <div className="h-9 bg-gray-200 rounded-xl w-36" />
        </div>
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="card p-6 space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/3" />
          <div className="h-3 bg-gray-100 rounded w-full" />
          <div className="h-3 bg-gray-100 rounded w-5/6" />
        </div>
      ))}
    </div>
  );
}

export default function CaseDetailPage() {
  const { id }   = useParams();
  const navigate = useNavigate();

  const [caseData,   setCaseData]   = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [addStatus,  setAddStatus]  = useState("idle"); // idle | loading | done | error
  const [addMsg,     setAddMsg]     = useState("");
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError,   setPdfError]   = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setPdfError("");
    getCaseDetail(id)
      .then((res) => setCaseData(res.data.data))
      .catch(() => setPdfError("Failed to load case details. Please try again."))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAddToRepo = async () => {
    setAddStatus("loading");
    setAddMsg("");
    try {
      const res = await addCaseToRepository(id);
      setAddStatus("done");
      setAddMsg(res.data.message || "Case added successfully to Legal Repository.");
    } catch (err) {
      setAddStatus("error");
      setAddMsg(err.response?.data?.detail || "Failed to add case to repository.");
    }
  };

  // Authenticated PDF download via axios blob — JWT token is sent automatically
  const handleDownloadPdf = async () => {
    setPdfLoading(true);
    setPdfError("");
    try {
      const res  = await api.get(`/research/case/${id}/download`, { responseType: "blob" });
      const url  = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href  = url;
      const safeName = (caseData?.title || id)
        .replace(/[^a-zA-Z0-9 ]/g, "")
        .replace(/ /g, "_")
        .slice(0, 60);
      link.setAttribute("download", `${safeName}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setPdfLoading(false);
    } catch (err) {
      setPdfLoading(false);
      // Handle JSON error response from backend
      if (err.response?.data?.message) {
        setPdfError(err.response.data.message);
      } else if (err.response?.status === 404) {
        setPdfError("Judgement PDF could not be generated.");
      } else if (err.response?.status === 500) {
        setPdfError("Server error while generating PDF.");
      } else {
        setPdfError("Download failed. Please try again.");
      }
    }
  };

  const handleOpenSimilar = (docId) => navigate(`/research/case/${docId}`);

  const has = (v) => v && String(v).trim().length > 0;

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-5">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-600 transition-colors">
          <ArrowLeft size={15} /> Back to Search
        </button>
        <Skeleton />
      </div>
    );
  }

  if (pdfError) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-600 transition-colors">
          <ArrowLeft size={15} /> Back to Search
        </button>
        <div className="card p-8 text-center">
          <div className="w-14 h-14 bg-red-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <AlertCircle size={24} className="text-red-500" />
          </div>
          <p className="font-semibold text-navy-600 mb-1">Could not load case</p>
          <p className="text-sm text-gray-400 mb-5">{pdfError}</p>
          <button onClick={() => navigate(-1)} className="btn-outline px-6 py-2.5 rounded-xl">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!caseData) return null;

  const strength    = caseData.ai_analysis?.precedent_strength?.toUpperCase();
  const strengthCfg = STRENGTH[strength] || STRENGTH.MEDIUM;

  return (
    <div className="max-w-4xl mx-auto space-y-5 pb-10">

      <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-600 transition-colors">
        <ArrowLeft size={15} /> Back to Search Results
      </button>

      {/* ── Hero card ──────────────────────────────────────────────────────── */}
      <div className="card p-7 space-y-5">
        {caseData.source === "indian_kanoon" && (
          <span className="badge bg-blue-50 text-blue-600 border border-blue-100 text-[10px]">
            Indian Kanoon
          </span>
        )}

        <h1 className="text-xl font-bold text-navy-600 leading-snug">{caseData.title}</h1>

        <div className="flex flex-wrap gap-3">
          {has(caseData.court) && (
            <span className="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg">
              <Building2 size={12} className="text-navy-500" /> {caseData.court}
            </span>
          )}
          {has(caseData.year) && (
            <span className="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg">
              <Calendar size={12} className="text-navy-500" /> {caseData.year}
            </span>
          )}
          {has(caseData.citation) && (
            <span className="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg">
              <Hash size={12} className="text-navy-500" /> {caseData.citation}
            </span>
          )}
          {has(caseData.judges) && (
            <span className="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg">
              <User size={12} className="text-navy-500" /> {caseData.judges}
            </span>
          )}
          {has(caseData.category) && (
            <span className="badge bg-navy-50 text-navy-600 border border-navy-100 text-[10px]">
              {caseData.category}
            </span>
          )}
        </div>

        {has(caseData.summary) && (
          <p className="text-sm text-gray-600 leading-relaxed border-l-4 border-gold-400 pl-4 bg-gold-50/40 py-2 rounded-r-lg">
            {caseData.summary}
          </p>
        )}

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3 pt-1">
          <button
            onClick={handleDownloadPdf}
            disabled={pdfLoading}
            className="btn-primary px-5 py-2.5 rounded-xl text-sm disabled:opacity-60"
          >
            {pdfLoading
              ? <><Loader size={14} className="animate-spin" /> Generating PDF...</>
              : <><Download size={15} /> Download PDF</>}
          </button>

          <button
            onClick={handleAddToRepo}
            disabled={addStatus === "loading" || addStatus === "done"}
            className={`inline-flex items-center gap-2 font-semibold text-sm px-5 py-2.5 rounded-xl border-2 transition-all disabled:opacity-60 ${
              addStatus === "done"
                ? "border-emerald-500 bg-emerald-50 text-emerald-700"
                : "border-navy-600 text-navy-600 hover:bg-navy-600 hover:text-white"
            }`}
          >
            {addStatus === "loading"
              ? <><Loader size={14} className="animate-spin" /> Adding...</>
              : addStatus === "done"
              ? <><CheckCircle size={15} /> Added to Repository</>
              : <><BookPlus size={15} /> Add to Repository</>}
          </button>

          <Link
            to={`/research?q=${encodeURIComponent(caseData.title)}`}
            className="btn-outline px-5 py-2.5 rounded-xl text-sm"
          >
            <Search size={15} /> Find Similar Cases
          </Link>

          {has(caseData.document_url) && (
            <a
              href={caseData.document_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-600 transition-colors px-3 py-2.5"
            >
              <ExternalLink size={14} /> View on Indian Kanoon
            </a>
          )}
        </div>

        {addMsg && (
          <div className={`flex items-center gap-2 text-sm rounded-xl px-4 py-3 ${
            addStatus === "done"
              ? "bg-emerald-50 border border-emerald-200 text-emerald-700"
              : "bg-red-50 border border-red-200 text-red-700"
          }`}>
            {addStatus === "done" ? <CheckCircle size={15} /> : <AlertCircle size={15} />}
            {addMsg}
          </div>
        )}

        {pdfError && (
          <div className="flex items-center gap-2 text-sm rounded-xl px-4 py-3 bg-red-50 border border-red-200 text-red-700">
            <AlertCircle size={15} />
            {pdfError}
          </div>
        )}
      </div>

      {/* ── Acts & Sections ───────────────────────────────────────────────── */}
      <Section icon={FileText} title="Acts and Sections Mentioned" hasContent={has(caseData.acts_sections)}>
        <ActsChips value={caseData.acts_sections} />
      </Section>

      {/* ── Facts ─────────────────────────────────────────────────────────── */}
      <Section icon={BookOpen} title="Facts of the Case" hasContent={has(caseData.case_facts)}>
        <TextBlock text={caseData.case_facts} />
      </Section>

      {/* ── Issues ────────────────────────────────────────────────────────── */}
      <Section icon={Lightbulb} title="Legal Issues Involved" hasContent={has(caseData.legal_issues)}>
        <TextBlock text={caseData.legal_issues} />
      </Section>

      {/* ── Arguments ─────────────────────────────────────────────────────── */}
      <Section icon={Scale} title="Arguments" defaultOpen={false} hasContent={has(caseData.arguments)}>
        <TextBlock text={caseData.arguments} />
      </Section>

      {/* ── Court Reasoning ───────────────────────────────────────────────── */}
      <Section icon={Gavel} title="Court Reasoning" defaultOpen={false} hasContent={has(caseData.court_reasoning)}>
        <TextBlock text={caseData.court_reasoning} />
      </Section>

      {/* ── Final Decision ────────────────────────────────────────────────── */}
      <Section icon={CheckCircle} title="Final Judgment / Order" accent hasContent={has(caseData.final_decision)}>
        <TextBlock text={caseData.final_decision} />
      </Section>

      {/* ── Full Judgment Text ────────────────────────────────────────────── */}
      <Section icon={FileText} title="Full Judgment Text" defaultOpen={false} hasContent={has(caseData.judgment_text)}>
        <div className="max-h-96 overflow-y-auto pr-2 border border-gray-100 rounded-xl p-4 bg-slate-50">
          <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap font-mono">
            {caseData.judgment_text}
          </p>
        </div>
      </Section>

      {/* ── AI Legal Analysis ─────────────────────────────────────────────── */}
      {caseData.ai_analysis && (
        <Section icon={Brain} title="AI Legal Analysis" accent hasContent>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <TrendingUp size={14} className="text-gray-500" />
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Precedent Strength</span>
              <span className={`badge border text-xs ${strengthCfg.cls}`}>{strength}</span>
              <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${strengthCfg.bar} ${strengthCfg.w}`} />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {has(caseData.ai_analysis.legal_issue) && (
                <div className="bg-slate-50 rounded-xl p-4">
                  <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1">Legal Issue</p>
                  <p className="text-sm text-gray-700">{caseData.ai_analysis.legal_issue}</p>
                </div>
              )}
              {has(caseData.ai_analysis.principle_established) && (
                <div className="bg-slate-50 rounded-xl p-4">
                  <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1">Legal Principle</p>
                  <p className="text-sm text-gray-700">{caseData.ai_analysis.principle_established}</p>
                </div>
              )}
              {has(caseData.ai_analysis.applicability) && (
                <div className="bg-slate-50 rounded-xl p-4">
                  <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1">Applicability</p>
                  <p className="text-sm text-gray-700">{caseData.ai_analysis.applicability}</p>
                </div>
              )}
              {has(caseData.ai_analysis.recommendation) && (
                <div className="bg-navy-50 rounded-xl p-4 border border-navy-100">
                  <p className="text-[10px] font-semibold text-navy-400 uppercase tracking-widest mb-1">Recommendation</p>
                  <p className="text-sm text-navy-700">{caseData.ai_analysis.recommendation}</p>
                </div>
              )}
            </div>
          </div>
        </Section>
      )}

      {/* ── Similar Cases ─────────────────────────────────────────────────── */}
      {caseData.similar_cases?.length > 0 && (
        <Section icon={Search} title={`Similar Cases (${caseData.similar_cases.length})`} hasContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {caseData.similar_cases.map((item, i) => (
              <SimilarCard key={item.id ?? i} item={item} onOpen={handleOpenSimilar} />
            ))}
          </div>
        </Section>
      )}

    </div>
  );
}
