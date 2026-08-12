import api from "./api";

export const getMe = () => api.get("/user/me");
