import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { customersApi, projectsApi, documentsApi, versionsApi, comparisonApi, dashboardApi } from '../api'

export function useCustomers() {
  return useQuery({ queryKey: ['customers'], queryFn: () => customersApi.list().then(r => r.data) })
}

export function useProjects(customerId: number | null) {
  return useQuery({
    queryKey: ['projects', customerId],
    queryFn: () => projectsApi.list(customerId!).then(r => r.data),
    enabled: customerId != null,
  })
}

export function useDocuments(projectId: number | null) {
  return useQuery({
    queryKey: ['documents', projectId],
    queryFn: () => documentsApi.list(projectId!).then(r => r.data),
    enabled: projectId != null,
    staleTime: 10_000,
  })
}

export function useVersions(documentId: number | null) {
  return useQuery({
    queryKey: ['versions', documentId],
    queryFn: () => versionsApi.list(documentId!).then(r => r.data),
    enabled: documentId != null,
  })
}

export function useComparison(versionAId: number | null, versionBId: number | null) {
  return useQuery({
    queryKey: ['comparison', versionAId, versionBId],
    queryFn: () => comparisonApi.compare(versionAId!, versionBId!).then(r => r.data),
    enabled: versionAId != null && versionBId != null,
  })
}

export function useLatestComparison(documentId: number | null) {
  return useQuery({
    queryKey: ['comparison-latest', documentId],
    queryFn: () => comparisonApi.latestForDocument(documentId!).then(r => r.data),
    enabled: documentId != null,
    retry: false,
  })
}

export function useDashboardStats() {
  return useQuery({ queryKey: ['stats'], queryFn: () => dashboardApi.stats().then(r => r.data) })
}

export function useActivity() {
  return useQuery({ queryKey: ['activity'], queryFn: () => dashboardApi.activity().then(r => r.data) })
}

export function useUploadDocument() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (formData: FormData) => documentsApi.upload(formData).then(r => r.data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['documents', data.document.project_id] })
      qc.invalidateQueries({ queryKey: ['stats'] })
      qc.invalidateQueries({ queryKey: ['activity'] })
    },
  })
}

export function useUploadBatch() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (formData: FormData) => documentsApi.uploadBatch(formData).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents'] })
      qc.invalidateQueries({ queryKey: ['stats'] })
      qc.invalidateQueries({ queryKey: ['activity'] })
    },
  })
}

export function useScanPath() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ path, projectId, changeSummary }: { path: string; projectId: number; changeSummary?: string }) =>
      documentsApi.scanPath(path, projectId, changeSummary).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents'] })
      qc.invalidateQueries({ queryKey: ['stats'] })
      qc.invalidateQueries({ queryKey: ['activity'] })
    },
  })
}

export function useCreateCustomer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => customersApi.create(name).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['customers'] }),
  })
}

export function useCreateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ customerId, name, description }: { customerId: number; name: string; description?: string }) =>
      projectsApi.create(customerId, name, description).then(r => r.data),
    onSuccess: (data) => qc.invalidateQueries({ queryKey: ['projects', data.customer_id] }),
  })
}
