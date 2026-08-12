import { useState, useRef } from "react";
import { uploadDocument } from "../../services/documentService";
import {
  Upload, FileText, CheckCircle, AlertCircle, CloudUpload,
  Brain, Scale, Shield, ArrowRight, X, Building2, Calendar
} from "lucide-react";

const CASE_TYPES = ["Civil", "Criminal", "Family", "Property", "Other"];

const DISCLAIMER = "This information is for general legal awareness and not a substitute for professional legal advice. Consult a qualified legal professional before taking any action.";

function SimilarCaseCard({ item }) {
  const pct = Math.round(item.similarity || 0);
  const color = pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-red-400";
  const badge = pct >= 75 ? "bg-emerald-100 text-emerald-700" : pct >= 50 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700";
  return (
    <div className="card p-4 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-navy-600 text-xs leading-snug flex-1">{item.title}</h3>
        <span className={`badge text-xs shrink-0 ${badge}`}>{pct}% match</span>
      </div>
      {item.court && (
        <span className="flex items-center gap-1 text-[10px] text-gray-500"><Building2 size={9} />{item.court}</span>
      )}
      {item.year && (
        <span className="flex items-center gap-1 text-[10px] text-gray-500 ml-2"><Calendar size={9} />{item.year}</span>
      )}
      {item.match_reason && <p className="text-xs text-gray-600 leading-relaxed">{item.match_reason}</p>}
      {item.description && <p className="text-xs text-gray-500 line-clamp-2">{item.description}</p>}
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function AnalysisResult({ result, caseType }) {
  const doc = result?.document || result;
  const similar = result?.similar_cases || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3">
        <CheckCircle size={16} className="text-emerald-600 shrink-0" />
        <p className="text-emerald-700 text-sm font-medium">Document analysed successfully</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* LEFT: Document Analysis */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <FileText size={16} className="text-navy-600" />
            <h2 className="font-bold text-navy-600 text-sm">Uploaded Document Analysis</h2>
          </div>
          <div className="space-y-2 text-xs">
            {doc?.title && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Document</p>
                <p className="text-navy-700 font-semibold mt-0.5">{doc.title}</p>
              </div>
            )}
            {caseType && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Case Type</p>
                <p className="text-navy-700 font-semibold mt-0.5">{caseType}</p>
              </div>
            )}
            {doc?.category && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Category</p>
                <p className="text-navy-700 font-semibold mt-0.5">{doc.category}</p>
              </div>
            )}
            {doc?.court && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Court</p>
                <p className="text-navy-700 font-semibold mt-0.5">{doc.court}</p>
              </div>
            )}
            {doc?.year && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Year</p>
                <p className="text-navy-700 font-semibold mt-0.5">{doc.year}</p>
              </div>
            )}
            {doc?.description && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Summary</p>
                <p className="text-navy-700 mt-0.5 leading-relaxed">{doc.description}</p>
              </div>
            )}
            {doc?.tags && (
              <div className="bg-navy-50 rounded-lg px-3 py-2">
                <p className="text-gray-500 font-medium">Keywords</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {doc.tags.split(",").map((t) => (
                    <span key={t} className="bg-emerald-100 text-emerald-700 text-[10px] px-1.5 py-0.5 rounded">{t.trim()}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* CENTER: Similar Cases */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Scale size={16} className="text-navy-600" />
            <h2 className="font-bold text-navy-600 text-sm">Similar Cases</h2>
            {similar.length > 0 && (
              <span className="badge bg-navy-50 text-navy-600 text-xs ml-auto">{similar.length}</span>
            )}
          </div>
          {similar.length > 0 ? (
            <div className="space-y-3">
              {similar.map((item, i) => <SimilarCaseCard key={i} item={item} />)}
            </div>
          ) : (
            <div className="text-center py-8">
              <Scale size={24} className="text-gray-300 mx-auto mb-2" />
              <p className="text-xs text-gray-400">No similar cases found in the database.</p>
            </div>
          )}
        </div>

        {/* RIGHT: AI Legal Guidance */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Brain size={16} className="text-navy-600" />
            <h2 className="font-bold text-navy-600 text-sm">AI Legal Guidance</h2>
          </div>
          <div className="space-y-3 text-xs">
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 space-y-1">
              <p className="font-semibold text-blue-700 flex items-center gap-1"><ArrowRight size={11} />How to Proceed</p>
              <p className="text-blue-600 leading-relaxed">
                Based on this document, review the identified acts and sections carefully. Consider consulting a legal professional to understand your options and the appropriate forum for your matter.
              </p>
            </div>
            <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 space-y-1">
              <p className="font-semibold text-amber-700 flex items-center gap-1"><ArrowRight size={11} />Appeal Information</p>
              <p className="text-amber-600 leading-relaxed">
                If you disagree with an order, you may consider filing an appeal before the appropriate appellate authority within the prescribed limitation period.
              </p>
            </div>
            <div className="bg-purple-50 border border-purple-100 rounded-xl p-3 space-y-1">
              <p className="font-semibold text-purple-700 flex items-center gap-1"><ArrowRight size={11} />Relevant Acts</p>
              <p className="text-purple-600 leading-relaxed">
                {doc?.tags
                  ? `Applicable provisions may relate to: ${doc.tags}`
                  : "Applicable provisions depend on the specific facts of your case. Refer to the similar cases above for relevant acts and sections."}
              </p>
            </div>
            <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 space-y-1">
              <p className="font-semibold text-emerald-700 flex items-center gap-1"><Shield size={11} />Constitutional Rights</p>
              <p className="text-emerald-600 leading-relaxed">
                Relevant constitutional provisions may include Articles 14 (Equality), 19 (Freedom), and 21 (Life and Personal Liberty) of the Constitution of India.
              </p>
            </div>
            <div className="bg-red-50 border border-red-100 rounded-xl p-3 space-y-1">
              <p className="font-semibold text-red-700 flex items-center gap-1"><AlertCircle size={11} />Important Precautions</p>
              <p className="text-red-600 leading-relaxed">Consult a legal professional before taking any action. Do not rely solely on AI-generated guidance for legal decisions.</p>
            </div>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-[10px] text-gray-500 leading-relaxed">
            ⚠️ {DISCLAIMER}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CitizenCaseAnalysisPage() {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [caseType, setCaseType] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const processFile = (f) => {
    if (!f) return;
    if (f.type !== "application/pdf") { setError("Only PDF files are allowed."); return; }
    if (f.size > 50 * 1024 * 1024) { setError("Maximum file size is 50 MB."); return; }
    setFile(f);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setResult(null);
    if (!file) { setError("Please select a PDF file."); return; }
    if (!caseType) { setError("Please select a case type."); return; }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name.replace(".pdf", "").replaceAll("_", " "));
    formData.append("category", "JUDGMENT");
    formData.append("description", description);
    formData.append("tags", caseType);

    setLoading(true);
    try {
      const res = await uploadDocument(formData);
      setResult(res.data.data);
    } catch (err) {
      setError(err.response?.data?.message || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="space-y-6">
        <div className="bg-navy-600 rounded-3xl p-7 relative overflow-hidden">
          <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none" />
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2">
              <Brain size={15} className="text-navy-300" />
              <span className="text-navy-300 text-xs font-semibold uppercase tracking-widest">Case Analysis</span>
            </div>
            <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
            <p className="text-navy-200 text-sm mt-1">AI-powered insights from your uploaded document</p>
          </div>
        </div>
        <AnalysisResult result={result} caseType={caseType} />
        <button
          onClick={() => { setResult(null); setFile(null); setCaseType(""); setDescription(""); }}
          className="btn-outline px-6 py-2.5 rounded-xl"
        >
          Analyse Another Document
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-navy-600 rounded-3xl p-7 relative overflow-hidden">
        <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Brain size={15} className="text-navy-300" />
            <span className="text-navy-300 text-xs font-semibold uppercase tracking-widest">Case Analysis</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Upload & Analyse Document</h1>
          <p className="text-navy-200 text-sm mt-1">Upload your legal document and get AI-powered insights</p>
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <span className="flex-1">{error}</span>
          <button onClick={() => setError("")}><X size={14} /></button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Step 1: Upload */}
        <div className="card p-6 space-y-4">
          <div>
            <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest">Step 1</p>
            <h2 className="font-semibold text-navy-600 text-sm mt-0.5">Upload Legal Document</h2>
            <p className="text-xs text-gray-400 mt-0.5">Court notice, FIR, legal notice, judgment — PDF only · Max 50 MB</p>
          </div>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); processFile(e.dataTransfer.files[0]); }}
            onClick={() => fileInputRef.current.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
              dragging ? "border-emerald-400 bg-emerald-50"
              : file ? "border-emerald-400 bg-emerald-50"
              : "border-gray-200 hover:border-emerald-400 hover:bg-slate-50"
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
                  <CloudUpload size={22} className="text-navy-400" />
                </div>
                <p className="text-sm text-gray-600"><span className="font-semibold text-navy-600">Click to browse</span> or drag & drop</p>
                <p className="text-xs text-gray-400 mt-1">PDF files only · Max 50 MB</p>
              </>
            )}
          </div>
        </div>

        {/* Step 2: Details */}
        <div className="card p-6 space-y-4">
          <div>
            <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest">Step 2</p>
            <h2 className="font-semibold text-navy-600 text-sm mt-0.5">Case Details</h2>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Case Type *</label>
            <div className="flex flex-wrap gap-2">
              {CASE_TYPES.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setCaseType(type)}
                  className={`px-4 py-2 rounded-xl border-2 text-xs font-medium transition-all ${
                    caseType === type
                      ? "border-emerald-600 bg-emerald-600 text-white"
                      : "border-gray-200 text-gray-600 hover:border-emerald-400"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Description of Issue (Optional)</label>
            <textarea
              className="input-field resize-none text-sm"
              rows={3}
              placeholder="Briefly describe your legal issue or what you need help with..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 rounded-2xl text-base">
          {loading ? (
            <><span className="spinner" /> Analysing Document...</>
          ) : (
            <><Brain size={17} /> Analyse Document</>
          )}
        </button>
      </form>
    </div>
  );
}
