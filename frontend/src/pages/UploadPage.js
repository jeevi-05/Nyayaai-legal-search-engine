import { useState, useRef } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { uploadDocument } from "../services/documentService";
import { getErrorMessage } from "../utils/helpers";
import {
  Upload, FileText, Scale, Gavel, CheckCircle,
  AlertCircle, CloudUpload, X
} from "lucide-react";

const CATEGORIES = [
  { value: "ACT",           label: "Act / Statute", icon: FileText },
  { value: "LANDMARK_CASE", label: "Landmark Case",  icon: Scale    },
  { value: "JUDGMENT",      label: "Judgment",       icon: Gavel    },
];

export default function UploadPage() {
  const { user }   = useAuth();
  const navigate   = useNavigate();
  const fileInputRef = useRef();

  const [file, setFile]       = useState(null);
  const [dragging, setDragging] = useState(false);
  const [form, setForm]       = useState({
    title: "", category: "ACT", description: "",
    citation: "", year: "", court: "", tags: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const [success, setSuccess] = useState("");

  if (user?.role !== "ADMIN") return <Navigate to="/repository" replace />;

  const handleChange = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const applyFile = (f) => {
    if (!f) return;
    setFile(f);
    if (!form.title) setForm((p) => ({ ...p, title: f.name.replace(".pdf", "").replace(/_/g, " ") }));
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === "application/pdf") applyFile(dropped);
    else setError("Only PDF files are accepted.");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    if (!file)             { setError("Please select a PDF file."); return; }
    if (!form.title.trim()) { setError("Title is required."); return; }

    const data = new FormData();
    data.append("file",    file);
    data.append("title",   form.title.trim());
    data.append("category", form.category);
    if (form.description) data.append("description", form.description);
    if (form.citation)    data.append("citation",    form.citation);
    if (form.year)        data.append("year",        form.year);
    if (form.court)       data.append("court",       form.court);
    if (form.tags)        data.append("tags",        form.tags);

    setLoading(true);
    try {
      await uploadDocument(data);
      setSuccess(`"${form.title}" uploaded successfully!`);
      setFile(null);
      setForm({ title: "", category: "ACT", description: "", citation: "", year: "", court: "", tags: "" });
      setTimeout(() => navigate("/repository"), 1800);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <p className="section-label">Admin · Repository</p>
        <h1 className="page-title">Upload Legal Document</h1>
        <p className="text-gray-500 text-sm mt-1">
          PDF files are stored in the dataset repository. Metadata is saved to the database.
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="flex items-start gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <span className="flex-1">{error}</span>
          <button onClick={() => setError("")}><X size={14} /></button>
        </div>
      )}
      {success && (
        <div className="flex items-start gap-2.5 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl px-4 py-3 text-sm">
          <CheckCircle size={16} className="shrink-0 mt-0.5" />
          {success} Redirecting...
        </div>
      )}

      <form onSubmit={handleSubmit} className="card p-7 space-y-6">

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
            dragging
              ? "border-gold-400 bg-gold-50"
              : file
              ? "border-emerald-400 bg-emerald-50"
              : "border-gray-200 hover:border-navy-400 hover:bg-slate-50"
          }`}
        >
          <input ref={fileInputRef} type="file" accept=".pdf"
            onChange={(e) => applyFile(e.target.files[0])} className="hidden" />
          {file ? (
            <>
              <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <FileText size={22} className="text-emerald-600" />
              </div>
              <p className="font-semibold text-emerald-700 text-sm">{file.name}</p>
              <p className="text-xs text-gray-400 mt-1">
                {(file.size / 1024 / 1024).toFixed(2)} MB · Click to change
              </p>
            </>
          ) : (
            <>
              <div className="w-12 h-12 bg-navy-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <CloudUpload size={22} className="text-navy-400" />
              </div>
              <p className="text-sm text-gray-600">
                <span className="font-semibold text-navy-600">Click to browse</span> or drag & drop
              </p>
              <p className="text-xs text-gray-400 mt-1">PDF files only · Max 50 MB</p>
            </>
          )}
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <div className="grid grid-cols-3 gap-2">
            {CATEGORIES.map(({ value, label, icon: Icon }) => (
              <button key={value} type="button"
                onClick={() => setForm((p) => ({ ...p, category: value }))}
                className={`flex flex-col items-center gap-1.5 py-3 rounded-xl border-2 text-sm font-medium transition-all ${
                  form.category === value
                    ? "border-navy-600 bg-navy-600 text-white"
                    : "border-gray-200 text-gray-600 hover:border-navy-400"
                }`}
              >
                <Icon size={17} />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Title *</label>
          <input name="title" value={form.title} onChange={handleChange}
            placeholder="e.g. Information Technology Act 2000"
            required className="input-field" />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
          <textarea name="description" value={form.description} onChange={handleChange}
            placeholder="Brief description of this document..."
            rows={3} className="input-field resize-none" />
        </div>

        {/* Citation + Year */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Citation</label>
            <input name="citation" value={form.citation} onChange={handleChange}
              placeholder="AIR 2000 SC 1234" className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Year</label>
            <input name="year" type="number" value={form.year} onChange={handleChange}
              placeholder="2000" min="1800" max="2100" className="input-field" />
          </div>
        </div>

        {/* Court */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Court</label>
          <input name="court" value={form.court} onChange={handleChange}
            placeholder="Supreme Court of India" className="input-field" />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Tags</label>
          <input name="tags" value={form.tags} onChange={handleChange}
            placeholder="criminal, ipc, offences (comma-separated)" className="input-field" />
        </div>

        {/* Submit */}
        <button type="submit" disabled={loading}
          className="btn-primary w-full py-3.5 rounded-2xl text-base">
          {loading ? (
            <><span className="spinner" /> Uploading...</>
          ) : (
            <><Upload size={17} /> Upload to Repository</>
          )}
        </button>
      </form>
    </div>
  );
}
