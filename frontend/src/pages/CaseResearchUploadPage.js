import { useState, useRef } from "react";
import { uploadDocument } from "../services/documentService";
import {
  Gavel, Upload, FileText, CheckCircle, AlertCircle,
  Building2, Calendar, Tag, Hash, Brain, X
} from "lucide-react";

const CASE_TYPES = [
  { label: "Act / Statute",  value: "ACT",           icon: FileText },
  { label: "Landmark Case",  value: "LANDMARK_CASE", icon: Gavel    },
  { label: "Judgment",       value: "JUDGMENT",       icon: Building2},
];

const COURTS = [
  "Supreme Court of India",
  "Delhi High Court",
  "Bombay High Court",
  "Madras High Court",
  "Karnataka High Court",
  "Other",
];

function SimilarCaseCard({ item }) {
  const pct = Math.round(item.similarity);
  const color = pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-red-400";
  const badge = pct >= 75 ? "bg-emerald-100 text-emerald-700" : pct >= 50 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700";

  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-navy-600 text-sm leading-snug">{item.title}</h3>
        <span className={`badge text-xs shrink-0 ${badge}`}>{pct}% match</span>
      </div>
      {item.category && (
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-lg inline-block">{item.category}</span>
      )}
      {item.match_reason && (
        <p className="text-xs text-gray-600 leading-relaxed">{item.match_reason}</p>
      )}
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function CaseResearchUploadPage() {
  const fileInputRef = useRef(null);
  const [file, setFile]       = useState(null);
  const [dragging, setDragging] = useState(false);
  const [form, setForm]       = useState({
    title: "", caseType: "", year: "", court: "",
    citation: "", tags: "", description: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const [success, setSuccess] = useState("");
  const [result, setResult]   = useState(null);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const processFile = (selected) => {
    if (!selected) return;
    if (selected.type !== "application/pdf") { setError("Only PDF files are allowed."); return; }
    if (selected.size > 50 * 1024 * 1024)   { setError("Maximum file size is 50 MB."); return; }
    setFile(selected);
    setError("");
    if (!form.title) {
      setForm((f) => ({ ...f, title: selected.name.replace(".pdf", "").replaceAll("_", " ") }));
    }
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    processFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess(""); setResult(null);
    if (!file)          { setError("Please select a PDF file."); return; }
    if (!form.title)    { setError("Case title is required."); return; }
    if (!form.caseType) { setError("Please select a case type."); return; }

    const formData = new FormData();
    formData.append("file",        file);
    formData.append("title",       form.title);
    formData.append("category",    form.caseType);
    formData.append("description", form.description);
    formData.append("citation",    form.citation);
    formData.append("year",        form.year);
    formData.append("court",       form.court);
    formData.append("tags",        form.tags);

    setLoading(true);
    try {
      const response = await uploadDocument(formData);
      setSuccess("Document uploaded and analysed successfully.");
      setResult(response.data.data);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.message || "Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <p className="section-label">Case Analysis</p>
        <h1 className="page-title">Case Research Upload</h1>
        <p className="text-gray-500 text-sm mt-1">
          Submit case documents for storage and AI-powered legal analysis
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
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">

        {/* Drop zone */}
        <div className="card p-6 space-y-4">
          <div>
            <h2 className="font-semibold text-navy-600 text-sm">Upload Case Document</h2>
            <p className="text-xs text-gray-400 mt-0.5">PDF format only · Maximum 50 MB</p>
          </div>

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
            <input ref={fileInputRef} type="file" accept=".pdf" hidden onChange={(e) => processFile(e.target.files[0])} />
            {file ? (
              <>
                <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <FileText size={22} className="text-emerald-600" />
                </div>
                <p className="font-semibold text-emerald-700 text-sm">{file.name}</p>
                <p className="text-xs text-gray-400 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB · Click to change</p>
              </>
            ) : (
              <>
                <div className="w-12 h-12 bg-navy-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <Upload size={22} className="text-navy-400" />
                </div>
                <p className="text-sm text-gray-600">
                  <span className="font-semibold text-navy-600">Click to browse</span> or drag & drop
                </p>
                <p className="text-xs text-gray-400 mt-1">PDF files only · Max 50 MB</p>
              </>
            )}
          </div>
        </div>

        {/* Case type selector */}
        <div className="card p-6 space-y-4">
          <h2 className="font-semibold text-navy-600 text-sm">Case Information</h2>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Case Type *</label>
            <div className="grid grid-cols-3 gap-2">
              {CASE_TYPES.map(({ label, value, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, caseType: value }))}
                  className={`flex flex-col items-center gap-1.5 py-3 rounded-xl border-2 text-xs font-medium transition-all ${
                    form.caseType === value
                      ? "border-navy-600 bg-navy-600 text-white"
                      : "border-gray-200 text-gray-600 hover:border-navy-400"
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Case Title *</label>
            <input name="title" value={form.title} onChange={handleChange}
              placeholder="e.g. Kesavananda Bharati v. State of Kerala"
              className="input-field" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">
                <span className="flex items-center gap-1"><Calendar size={11} /> Year</span>
              </label>
              <input name="year" value={form.year} onChange={handleChange}
                placeholder="1973" type="number" min="1800" max="2100" className="input-field" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">
                <span className="flex items-center gap-1"><Hash size={11} /> Citation</span>
              </label>
              <input name="citation" value={form.citation} onChange={handleChange}
                placeholder="AIR 1973 SC 1461" className="input-field" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              <span className="flex items-center gap-1"><Building2 size={11} /> Court</span>
            </label>
            <select name="court" value={form.court} onChange={handleChange} className="input-field">
              <option value="">Select Court</option>
              {COURTS.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              <span className="flex items-center gap-1"><Tag size={11} /> Keywords / Tags</span>
            </label>
            <input name="tags" value={form.tags} onChange={handleChange}
              placeholder="constitutional, fundamental rights, amendment (comma-separated)"
              className="input-field" />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Case Summary</label>
            <textarea name="description" value={form.description} onChange={handleChange}
              placeholder="Brief summary of the case, key issues, and legal questions involved..."
              rows={4} className="input-field resize-none" />
          </div>
        </div>

        {/* Submit */}
        <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 rounded-2xl text-base">
          {loading ? (
            <><span className="spinner" /> Uploading & Analysing...</>
          ) : (
            <><Upload size={17} /> Upload Case Document</>
          )}
        </button>
      </form>

      {/* Similar cases results */}
      {result?.similar_cases?.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-navy-600" />
            <h2 className="font-bold text-navy-600">Similar Cases Found</h2>
            <span className="badge bg-navy-50 text-navy-600 ml-1">{result.similar_cases.length}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.similar_cases.map((item) => (
              <SimilarCaseCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
