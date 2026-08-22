import api from "../api/axios";

export const listJudgeJudgments = (params) => api.get("/judge/judgments", { params });
export const compareJudgments = (case1_id, case2_id) => api.post("/judge/judgment-comparison", { case1_id, case2_id });
export const analyzePrecedents = (issue) => api.post("/judge/precedent-analysis", { issue });
export const getLegalReasoning = (caseId) => api.get(`/judge/legal-reasoning/${caseId}`);
export const synthesizeCaseLaw = (topic) => api.post("/judge/case-law-synthesis", { topic });
