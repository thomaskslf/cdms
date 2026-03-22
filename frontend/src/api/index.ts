import client from './client'
import type {
  Customer, Project, Document, DocumentVersion,
  TokenResponse, UploadResponse, ComparisonResult, ActivityEntry,
} from '../types'

// Auth
export const authApi = {
  login: (username: string, password: string) => {
    const form = new FormData()
    form.append('username', username)
    form.append('password', password)
    return client.post<TokenResponse>('/auth/login', form)
  },
  me: () => client.get<TokenResponse['user']>('/auth/me'),
  setup: (username: string, email: string, password: string) =>
    client.post('/auth/setup', { username, email, password }),
  register: (data: { username: string; email: string; password: string; is_admin: boolean }) =>
    client.post('/auth/register', data),
}

// Customers
export const customersApi = {
  list: () => client.get<Customer[]>('/customers/'),
  create: (name: string) => client.post<Customer>('/customers/', { name }),
  update: (id: number, name: string) => client.put<Customer>(`/customers/${id}`, { name }),
  delete: (id: number) => client.delete(`/customers/${id}`),
}

// Projects
export const projectsApi = {
  list: (customerId: number) => client.get<Project[]>(`/customers/${customerId}/projects`),
  create: (customerId: number, name: string, description?: string) =>
    client.post<Project>(`/customers/${customerId}/projects`, { name, description }),
  delete: (projectId: number) => client.delete(`/projects/${projectId}`),
}

// Documents
export const documentsApi = {
  list: (projectId: number) => client.get<Document[]>(`/projects/${projectId}/documents`),
  get: (documentId: number) => client.get<Document>(`/documents/${documentId}`),
  upload: (formData: FormData) =>
    client.post<UploadResponse>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  uploadBatch: (formData: FormData) =>
    client.post<UploadResponse[]>('/documents/upload-batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  scanPath: (path: string, projectId: number, changeSummary?: string) =>
    client.post<UploadResponse[]>('/documents/scan-path', { path, project_id: projectId, change_summary: changeSummary }),
}

// Versions
export const versionsApi = {
  list: (documentId: number) => client.get<DocumentVersion[]>(`/documents/${documentId}/versions`),
  get: (versionId: number) => client.get<DocumentVersion>(`/versions/${versionId}`),
  downloadUrl: (versionId: number) => `/api/versions/${versionId}/download`,
  setCurrent: (versionId: number) => client.post(`/versions/${versionId}/set-current`),
  delete: (versionId: number) => client.delete(`/versions/${versionId}`),
}

// Comparison
export const comparisonApi = {
  compare: (versionAId: number, versionBId: number) =>
    client.post<ComparisonResult>('/comparison/compare', { version_a_id: versionAId, version_b_id: versionBId }),
  latestForDocument: (documentId: number) =>
    client.get<ComparisonResult>(`/comparison/document/${documentId}/latest`),
}

// Dashboard
export const dashboardApi = {
  stats: () => client.get<{ customers: number; projects: number; documents: number; versions: number }>('/dashboard/stats'),
  activity: (limit = 20) => client.get<ActivityEntry[]>(`/dashboard/activity?limit=${limit}`),
}
