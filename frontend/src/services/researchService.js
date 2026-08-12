import api from "../api/axios";

export const searchCases = async (query) =>
  api.get("/research/search", { params: { query } });

export const getCaseDetail = async (externalId) =>
  api.get(`/research/case/${externalId}`);

export const addCaseToRepository = async (externalId) =>
  api.post(`/research/case/${externalId}/add-to-repository`);

export const getCasePdfUrl = (externalId) =>
  `http://localhost:8000/api/research/case/${externalId}/download`;
