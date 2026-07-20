import axios from "axios";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const api = axios.create({
  baseURL: API_BASE_URL,
});

export async function analyzePortfolio(payload) {
  const response = await api.post("/api/portfolio/analyze", payload);
  return response.data;
}

export async function createPortfolio(payload) {
  const response = await api.post("/api/portfolio", payload);
  return response.data;
}

export async function listPortfolios() {
  const response = await api.get("/api/portfolio");
  return response.data;
}

export async function getPortfolio(portfolioId) {
  const response = await api.get(`/api/portfolio/${portfolioId}`);
  return response.data;
}

export async function updatePortfolio(portfolioId, payload) {
  const response = await api.patch(`/api/portfolio/${portfolioId}`, payload);
  return response.data;
}

export async function deletePortfolio(portfolioId) {
  const response = await api.delete(`/api/portfolio/${portfolioId}`);
  return response.data;
}

export async function updateHolding(holdingId, payload) {
  const response = await api.patch(
    `/api/portfolio/holdings/${holdingId}`,
    payload
  );
  return response.data;
}

export async function deleteHolding(holdingId) {
  const response = await api.delete(
    `/api/portfolio/holdings/${holdingId}`
  );
  return response.data;
}