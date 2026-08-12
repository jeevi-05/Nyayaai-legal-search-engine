import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useMode } from "../context/ModeContext";
import { getAllDocuments, deleteDocument } from "../services/documentService";
import { useAuth } from "../hooks/useAuth";
import { getErrorMessage } from "../utils/helpers";
import {
  BookOpen, FileText, Scale, Gavel, Upload, Trash2,
  Calendar, Building2, Tag, AlertCircle, FolderOpen, Hash
} from "lucide-react";

const CATEGORIES = ["ALL", "ACT", "LANDMARK_CASE", "JUDGMENT"];

const CATEGORY_META = {
  ALL:           { label: "All Documents",   icon: BookOpen, color: "text-navy-600",   bg: "bg-navy-50"   },
  ACT:           { label: "Acts",            icon: FileText, color: "text-blue-600",   bg: "bg-blue-50"   },
  LANDMARK_CASE: { label: "Landmark Cases",  icon: Scale,    color: "text-purple-600", bg: "bg-purple-50" },
  JUDGMENT:      { label: "Judgments",       icon: Gavel,    color: "text-emerald-600",bg: "bg-emerald-50"},
};

const BADGE_STYLE = {
  ACT:           "bg-blue-100 text-blue-700 border-blue-200",
  LANDMARK_CASE: "bg-purple-100 text-purple-700 border-purple-200",
  JUDGMENT:      "bg-emerald-100 text-emerald-700 border-emerald-200",
};

function DocumentCard({ doc, isAdmin, onDelete }) {
  const [deleting, setDeleting] = useState(false);
  const meta = CATEGORY_META[doc.category] || CATEGORY_META.JUDGMENT;
  const Icon = meta.icon;

  const handleDelete = async () => {
    if (!window.confirm(`Delete "${doc.title}"?`)) return;
    setDeleting(true);
    try { await onDelete(doc.id); }
    finally { setDeleting(false); }
  };

  return (
    <div className="card p-5 group flex flex-col gap-3 hover:border-gold-400">
      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${meta.bg}`}>
          <Icon size={16} className={meta.color} strokeWidth={2} />
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className={`badge border text-[10px] ${BADGE_STYLE[doc.category] || "bg-gray-100 text-gray-600 border-gray-200"}`}>
            {CATEGORY_META[doc.category]?.label || doc.category}
          </span>
          {isAdmin && (
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="text-gray-300 hover:text-red-500 transition-colors disabled:opacity-50"
              title="Delete document"
            >
              {deleting
                ? <span className="spinner text-red-400" style={{ width: 14, height: 14 }} />
                : <Trash2 size={14} />}
            </button>
          )}
        </div>
      </div>

      {/* Title */}
      <div>
        <h3 className="font-semibold text-navy-600 text-sm leading-snug group-hover:text-gold-500 transition-colors line-clamp-2">
          {doc.title}
        </h3>
        {doc.citation && (
          <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
            <Hash size={10} /> {doc.citation}
          </p>
        )}
      </div>

      {/* Description */}
      {doc.description && (
        <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">{doc.description}</p>
      )}

      {/* Meta chips */}
      <div className="flex flex-wrap gap-1.5 mt-auto">
        {doc.year && (
          <span className="flex items-center gap-1 text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded-lg">
            <Calendar size={9} /> {doc.year}
          </span>
        )}
        {doc.court && (
          <span className="flex items-center gap-1 text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded-lg max-w-[160px] truncate">
            <Building2 size={9} /> {doc.court}
          </span>
        )}
        {doc.fileType && (
          <span className="flex items-center gap-1 text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded-lg">
            <FileText size={9} /> {doc.fileType}
          </span>
        )}
      </div>

      {/* Tags */}
      {doc.tags && (
        <div className="flex flex-wrap gap-1">
          {doc.tags.split(",").slice(0, 4).map((tag) => (
            <span key={tag} className="flex items-center gap-0.5 text-[10px] bg-navy-50 text-navy-600 px-1.5 py-0.5 rounded-md">
              <Tag size={8} /> {tag.trim()}
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
      <div className="flex gap-2">
        <div className="w-9 h-9 bg-gray-200 rounded-xl" />
        <div className="h-5 bg-gray-200 rounded w-20 ml-auto" />
      </div>
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-100 rounded w-full" />
      <div className="h-3 bg-gray-100 rounded w-2/3" />
      <div className="flex gap-1.5">
        <div className="h-5 w-12 bg-gray-100 rounded-lg" />
        <div className="h-5 w-24 bg-gray-100 rounded-lg" />
      </div>
    </div>
  );
}

export default function RepositoryPage() {
  const { mode } = useMode();
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";

  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState("ALL");
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");

  const fetchDocuments = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getAllDocuments();
      setDocuments(res.data.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocuments(); }, []);

  const handleDelete = async (id) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      alert(getErrorMessage(err));
    }
  };

  const filtered  = activeTab === "ALL" ? documents : documents.filter((d) => d.category === activeTab);
  const countFor  = (cat) => cat === "ALL" ? documents.length : documents.filter((d) => d.category === cat).length;

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p className="section-label">Knowledge Base</p>
          <h1 className="page-title">Legal Repository</h1>
          <p className="text-gray-500 text-sm mt-1">
            {loading ? "Loading..." : `${documents.length} document${documents.length !== 1 ? "s" : ""} in the repository`}
          </p>
        </div>
        {isAdmin && (
          <Link to="/upload" className="btn-primary shrink-0">
            <Upload size={15} /> Upload Document
          </Link>
        )}
      </div>

      {/* Category tabs */}
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
              <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
                active ? "bg-white/20 text-white" : "bg-gray-100 text-gray-500"
              }`}>
                {countFor(cat)}
              </span>
            </button>
          );
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-20 card">
          <div className="w-16 h-16 bg-navy-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FolderOpen size={28} className="text-navy-400" />
          </div>
          <p className="font-semibold text-navy-600 mb-1">No documents found</p>
          <p className="text-sm text-gray-400 mb-4">No documents in this category yet.</p>
          {isAdmin && (
            <Link to="/upload" className="btn-primary inline-flex">
              <Upload size={14} /> Upload Document
            </Link>
          )}
        </div>
      )}

      {/* Grid */}
      {!loading && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((doc) => (
            <DocumentCard key={doc.id} doc={doc} isAdmin={isAdmin} onDelete={handleDelete} />
          ))}
        </div>
      )}

    </div>
  );
}
