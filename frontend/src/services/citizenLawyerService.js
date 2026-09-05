import api from "../api/axios";

export const searchCitizenLawyers = (params) => api.get("/citizen/lawyers/search", { params });
export const getCitizenLawyer = (lawyerId) => api.get(`/citizen/lawyers/profile/${encodeURIComponent(lawyerId)}`);
export const getCitizenCase = (cnr) => api.get(`/citizen/lawyers/case/${encodeURIComponent(cnr)}`);
