import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useDocuments } from '../hooks'
import CategoryBadge from '../components/documents/CategoryBadge'
import DropZone from '../components/upload/DropZone'
import { Upload, FileText, ChevronRight, Star } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import type { DocType } from '../types'
import { ALL_DOC_TYPES, DOC_TYPE_LABELS } from '../types'

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const pid = parseInt(projectId!)
  const { data: documents = [], refetch } = useDocuments(pid)
  const [showUpload, setShowUpload] = useState(false)
  const [filterType, setFilterType] = useState<DocType | 'all'>('all')

  const filtered = filterType === 'all' ? documents : documents.filter(d => d.doc_type === filterType)

  // Group by doc_type
  const groups = ALL_DOC_TYPES.map(type => ({
    type,
    docs: filtered.filter(d => d.doc_type === type),
  })).filter(g => g.docs.length > 0 || filterType === 'all')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Projekt-Dokumente</h1>
          <p className="text-sm text-gray-500">{documents.length} Dokument(e)</p>
        </div>
        <button
          onClick={() => setShowUpload(v => !v)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          <Upload className="w-4 h-4" />
          Dokument hinzufügen
        </button>
      </div>

      {showUpload && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-medium text-gray-800 mb-4">Dokument(e) hochladen</h3>
          <DropZone projectId={pid} onSuccess={() => { setShowUpload(false); refetch() }} />
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilterType('all')}
          className={`text-sm px-3 py-1 rounded-full border ${filterType === 'all' ? 'bg-gray-900 text-white border-gray-900' : 'border-gray-200 text-gray-600 hover:border-gray-400'}`}
        >
          Alle
        </button>
        {ALL_DOC_TYPES.map(type => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`text-sm px-3 py-1 rounded-full border ${filterType === type ? 'bg-gray-900 text-white border-gray-900' : 'border-gray-200 text-gray-600 hover:border-gray-400'}`}
          >
            {DOC_TYPE_LABELS[type]} ({documents.filter(d => d.doc_type === type).length})
          </button>
        ))}
      </div>

      {documents.length === 0 ? (
        <div className="bg-white border border-dashed border-gray-300 rounded-xl p-12 text-center">
          <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Noch keine Dokumente. Lade das erste Dokument hoch.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {groups.map(group => (
            <div key={group.type}>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                {DOC_TYPE_LABELS[group.type]}
              </h3>
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                {group.docs.map((doc, i) => (
                  <Link
                    key={doc.id}
                    to={`/documents/${doc.id}`}
                    className={`flex items-center gap-4 px-4 py-3 hover:bg-gray-50 ${i > 0 ? 'border-t border-gray-100' : ''}`}
                  >
                    <FileText className="w-5 h-5 text-gray-400 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 text-sm truncate">{doc.name}</span>
                        <CategoryBadge docType={doc.doc_type} />
                        {doc.version_count > 1 && (
                          <span className="text-xs text-gray-400">{doc.version_count} Versionen</span>
                        )}
                      </div>
                      {doc.current_version && (
                        <div className="flex items-center gap-3 mt-0.5">
                          <span className="flex items-center gap-1 text-xs text-blue-600">
                            <Star className="w-3 h-3" /> v{doc.current_version.version_number}
                          </span>
                          <span className="text-xs text-gray-400">
                            {doc.current_version.uploader_username} •{' '}
                            {format(new Date(doc.current_version.uploaded_at), 'dd.MM.yyyy', { locale: de })}
                          </span>
                          {doc.current_version.change_summary && (
                            <span className="text-xs text-gray-500 italic truncate">{doc.current_version.change_summary}</span>
                          )}
                        </div>
                      )}
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 shrink-0" />
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
