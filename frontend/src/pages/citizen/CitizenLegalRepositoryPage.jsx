import { useEffect, useState } from "react";
import { getAllDocuments } from "../../services/documentService";
import { getErrorMessage } from "../../utils/helpers";
import {
  BookOpen, FileText, Scale, Gavel, Calendar,
  Building2, Tag, AlertCircle, FolderOpen, Hash
} from "lucide-react";

const CATEGORIES = ["ALL", "ACT", "LANDMARK_CASE", "JUDGMENT"];

const CATEGORY_META = {
  ALL:           { label: "All Documents",  icon: BookOpen, color: "text-navy-600",   bg: "bg-navy-50"   },
  ACT:           { label: "Acts",           icon: FileText, color: "text-blue-600",   bg: "bg-blue-50"   },
  LANDMARK_CASE: { label: "Landmark Cases", icon: Scale,    color: "text-purple-600", bg: "bg-purple-50" },
  JUDGMENT:      { label: "Judgments",      icon: Gavel,    color: "text-emerald-600",bg: "bg-emerald-50"},
};

const BADGE_STYLE = {
  ACT:           "bg-blue-100 text-blue-700 border-blue-200",
  LANDMARK_CASE: "bg-purple-100 text-purple-700 border-purple-200",
  JUDGMENT:      "bg-emerald-100 text-emerald-700 border-emerald-200",
};

function DocumentCard({ doc }) {
  const meta = CATEGORY_META[doc.category] || CATEGORY_META.JUDGMENT;
  const Icon = meta.icon;
  return (
    <div className="card p-5 flex flex-col gap-3 hover:border-emerald-400 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${meta.bg}`}>
          <Icon size={16} className={meta.color} strokeWidth={2} />
        </div>
        <span className={`badge border text-[10px] ml-auto ${BADGE_STYLE[doc.category] || "bg-gray-100 text-gray-600 border-gray-200"}`}>
          {CATEGORY_META[doc.category]?.label || doc.category}
        </span>
      </div>
      <div>
        <h3 className="font-semibold text-navy-600 text-sm leading-snug line-clamp-2">{doc.title}</h3>
        {doc.citation && (
          <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1"><Hash size={10} />{doc.citation}</p>
        )}
      </div>
      {doc.description && (
        <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">{doc.description}</p>
      )}
      <div className="flex flex-wrap gap-1.5 mt-auto">
        {doc.year && (
          <span className="flex items-center gap-1 text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded-lg">
            <Calendar size={9} />{doc.year}
          </span>
        )}
        {doc.court && (
          <span className="flex items-center gap-1 text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded-lg max-w-[160px] truncate">
            <Building2 size={9} />{doc.court}
          </span>
        )}
      </div>
      {doc.tags && (
        <div className="flex flex-wrap gap-1">
          {doc.tags.split(",").slice(0, 3).map((tag) => (
            <span key={tag} className="flex items-center gap-0.5 text-[10px] bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded-md">
              <Tag size={8} />{tag.trim()}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="card p-5 space-y-3 animate-pulse">
      <div className="flex gap-2"><div className="w-9 h-9 bg-gray-200 rounded-xl" /><div className="h-5 bg-gray-200 rounded w-20 ml-auto" /></div>
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-100 rounded w-full" />
      <div className="flex gap-1.5"><div className="h-5 w-12 bg-gray-100 rounded-lg" /><div className="h-5 w-24 bg-gray-100 rounded-lg" /></div>
    </div>
  );
}

export default function CitizenLegalRepositoryPage() {
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAllDocuments()
      .then((res) => setDocuments(res.data.data || []))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const filtered = activeTab === "ALL" ? documents : documents.filter((d) => d.category === activeTab);
  const countFor = (cat) => cat === "ALL" ? documents.length : documents.filter((d) => d.category === cat).length;

  return (
    <div className="space-y-6">
      <div className="bg-navy-600 rounded-3xl p-7 relative overflow-hidden">
        <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen size={15} className="text-navy-300" />
            <span className="text-navy-300 text-xs font-semibold uppercase tracking-widest">Legal Repository</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Legal Knowledge Library</h1>
          <p className="text-navy-200 text-sm mt-1">
            {loading ? "Loading..." : `${documents.length} document${documents.length !== 1 ? "s" : ""} — Acts, Landmark Cases & Judgments`}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => {
          const meta = CATEGORY_META[cat];
          const Icon = meta.icon;
          const active = activeTab === cat;
          return (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all border ${
                active
                  ? "bg-navy-600 text-white border-navy-600 shadow-sm"
                  : "bg-white text-gray-600 border-gray-200 hover:border-navy-400 hover:text-navy-600"
              }`}
            >
              <Icon size={14} />
              {meta.label}
              <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${active ? "bg-white/20 text-white" : "bg-gray-100 text-gray-500"}`}>
                {countFor(cat)}
              </span>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0" />{error}
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-20 card">
          <div className="w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FolderOpen size={28} className="text-emerald-400" />
          </div>
          <p className="font-semibold text-navy-600 mb-1">No documents found</p>
          <p className="text-sm text-gray-400">No documents in this category yet.</p>
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((doc) => <DocumentCard key={doc.id} doc={doc} />)}
        </div>
      )}
    </div>
  );
}
