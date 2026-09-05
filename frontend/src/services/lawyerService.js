import api from "../api/axios";

export const advancedResearch = (query, filters) => api.post("/lawyer/advanced-research", { query, filters });
export const analyzeArgument = (argument) => api.post("/lawyer/argument-research", { argument });
export const findCitations = (proposition) => api.post("/lawyer/citation-finder", { proposition });
export const getCaseBrief = (caseId) => api.get(`/lawyer/case-brief/${caseId}`);
export const findSimilarCases = (caseData) => api.post("/lawyer/case-similarity", caseData);
