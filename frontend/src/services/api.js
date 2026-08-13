import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Analysis APIs
export const analyzeText = async (text, documentName = null) => {
  const response = await api.post('/analyze', {
    text,
    document_name: documentName,
  });
  return response.data;
};

export const analyzeFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/analyze/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalysisHistory = async (skip = 0, limit = 20) => {
  const response = await api.get(`/analyze/history?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getAnalysisDetail = async (analysisId) => {
  const response = await api.get(`/analyze/history/${analysisId}`);
  return response.data;
};

export const deleteAnalysis = async (analysisId) => {
  const response = await api.delete(`/analyze/history/${analysisId}`);
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/analyze/statistics');
  return response.data;
};

// Document APIs
export const getDocuments = async (skip = 0, limit = 100) => {
  const response = await api.get(`/documents?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getDocument = async (documentId) => {
  const response = await api.get(`/documents/${documentId}`);
  return response.data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadMultipleDocuments = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await api.post('/documents/upload-multiple', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

export const searchDocuments = async (query) => {
  const response = await api.get(`/documents/search/${query}`);
  return response.data;
};

export const getDocumentStatistics = async () => {
  const response = await api.get('/documents/statistics/summary');
  return response.data;
};

// Report APIs
export const generateReport = async (analysisId, format = 'pdf') => {
  const response = await api.post('/reports/generate', {
    analysis_id: analysisId,
    report_format: format,
  });
  return response.data;
};

export const downloadReport = (reportId) => {
  return `${API_BASE_URL}/reports/download/${reportId}`;
};

export const getReportsForAnalysis = async (analysisId) => {
  const response = await api.get(`/reports/analysis/${analysisId}`);
  return response.data;
};

export const getAllReports = async (skip = 0, limit = 50) => {
  const response = await api.get(`/reports?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const deleteReport = async (reportId) => {
  const response = await api.delete(`/reports/${reportId}`);
  return response.data;
};

export const generateQuickReport = async (analysisId) => {
  return `${API_BASE_URL}/reports/generate-quick?analysis_id=${analysisId}`;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
