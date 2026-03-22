export interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Customer {
  id: number
  name: string
  slug: string
  created_at: string
}

export interface Project {
  id: number
  customer_id: number
  name: string
  slug: string
  description: string | null
  created_at: string
}

export type DocType =
  | 'zeichnung'
  | 'stückliste'
  | 'bestückzeichnung'
  | 'montagezeichnung'
  | 'key_anweisung'
  | 'unterbaugruppe'

export type DocumentStatus = 'current' | 'outdated' | 'needs_review'

export interface DocumentVersion {
  id: number
  document_id: number
  version_number: string
  version_label: string | null
  file_name: string
  file_size: number
  mime_type: string
  uploader_id: number
  uploader_username: string | null
  uploaded_at: string
  change_summary: string | null
  is_current: boolean
  thumbnail_path: string | null
}

export interface Document {
  id: number
  project_id: number
  doc_type: DocType
  name: string
  description: string | null
  status: DocumentStatus
  current_version_id: number | null
  current_version: DocumentVersion | null
  created_at: string
  version_count: number
}

export interface ClassificationResult {
  doc_type: DocType
  confidence: number
  needs_override: boolean
}

export interface UploadResponse {
  version: DocumentVersion
  document: Document
  classification: ClassificationResult
  is_duplicate: boolean
  auto_comparison_id: number | null
}

export interface ComparisonResult {
  id: number
  version_a_id: number
  version_b_id: number
  comparison_type: 'text' | 'bom' | 'dxf'
  diff_data: Record<string, unknown>
  summary: string
  computed_at: string
}

export interface ActivityEntry {
  id: number
  action: string
  entity_type: string
  entity_id: number
  created_at: string
  metadata: Record<string, string> | null
  username: string
}

export const DOC_TYPE_LABELS: Record<DocType, string> = {
  zeichnung:        'Zeichnung',
  stückliste:       'Stückliste',
  bestückzeichnung: 'Bestückzeichnung',
  montagezeichnung: 'Montagezeichnung',
  key_anweisung:    'Key-Anweisung',
  unterbaugruppe:   'Unterbaugruppe',
}

export const DOC_TYPE_COLORS: Record<DocType, string> = {
  zeichnung:        'bg-blue-100 text-blue-800',
  stückliste:       'bg-green-100 text-green-800',
  bestückzeichnung: 'bg-purple-100 text-purple-800',
  montagezeichnung: 'bg-orange-100 text-orange-800',
  key_anweisung:    'bg-red-100 text-red-800',
  unterbaugruppe:   'bg-yellow-100 text-yellow-800',
}

export const ALL_DOC_TYPES: DocType[] = [
  'zeichnung', 'stückliste', 'bestückzeichnung',
  'montagezeichnung', 'key_anweisung', 'unterbaugruppe',
]
