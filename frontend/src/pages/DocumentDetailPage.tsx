import { useParams, Link } from 'react-router-dom'
import { useVersions, useLatestComparison } from '../hooks'
import { documentsApi } from '../api'
import { useQuery } from '@tanstack/react-query'
import VersionTimeline from '../components/versions/VersionTimeline'
import ComparisonViewer from '../components/comparison/ComparisonViewer'
import CategoryBadge from '../components/documents/CategoryBadge'
import { ChevronLeft, GitCompare } from 'lucide-react'
import { useState } from 'react'

export default function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const did = parseInt(documentId!)
  const [showDiff, setShowDiff] = useState(false)

  const { data: doc } = useQuery({
    queryKey: ['document', did],
    queryFn: () => documentsApi.get(did).then(r => r.data),
  })

  const { data: versions = [] } = useVersions(did)
  const { data: latestComparison } = useLatestComparison(did)

  if (!doc) return <div className="text-gray-400 text-sm">Lade...</div>

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-2">
        <Link
          to={`/projects/${doc.project_id}`}
          className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1"
        >
          <ChevronLeft className="w-4 h-4" />
          Zurück zum Projekt
        </Link>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{doc.name}</h1>
          <div className="flex items-center gap-3 mt-2">
            <CategoryBadge docType={doc.doc_type} />
            <span className="text-sm text-gray-500">{versions.length} Version(en)</span>
          </div>
        </div>
        {latestComparison && (
          <button
            onClick={() => setShowDiff(v => !v)}
            className="flex items-center gap-2 text-sm border border-gray-200 rounded-lg px-3 py-2 hover:border-blue-300 hover:text-blue-600"
          >
            <GitCompare className="w-4 h-4" />
            {showDiff ? 'Diff ausblenden' : 'Letzten Diff zeigen'}
          </button>
        )}
      </div>

      {showDiff && latestComparison && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-medium text-gray-800 mb-4">Änderungen zur vorherigen Version</h3>
          <ComparisonViewer result={latestComparison} />
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h3 className="font-medium text-gray-800 mb-4">Versionsverlauf</h3>
        {versions.length > 0 ? (
          <VersionTimeline versions={versions} documentId={did} />
        ) : (
          <p className="text-gray-400 text-sm text-center py-6">Keine Versionen vorhanden</p>
        )}
      </div>
    </div>
  )
}
