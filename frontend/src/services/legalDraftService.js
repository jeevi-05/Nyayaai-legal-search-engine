import api from "../api/axios";

export const generateLegalDraft = (payload) => api.post("/citizen/legal-drafts/generate", payload);
export const downloadLegalDraftPdf = (draft) => api.post("/citizen/legal-drafts/pdf", { draft }, { responseType: "blob" });
