import { useParams, Link } from 'react-router-dom'
import { useComparison } from '../hooks'
import { versionsApi } from '../api'
import { useQuery } from '@tanstack/react-query'
import ComparisonViewer from '../components/comparison/ComparisonViewer'
import { ChevronLeft, Download } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'

export default function ComparisonPage() {
  const { versionAId, versionBId } = useParams<{ versionAId: string; versionBId: string }>()
  const aId = parseInt(versionAId!)
  const bId = parseInt(versionBId!)

  const { data: comparison, isLoading, error } = useComparison(aId, bId)

  const { data: vA } = useQuery({
    queryKey: ['version', aId],
    queryFn: () => versionsApi.get(aId).then(r => r.data),
  })
  const { data: vB } = useQuery({
    queryKey: ['version', bId],
    queryFn: () => versionsApi.get(bId).then(r => r.data),
  })

  return (
    <div className="space-y-6 max-w-4xl">
      <Link to={-1 as any} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1">
        <ChevronLeft className="w-4 h-4" /> Zurück
      </Link>

      <h1 className="text-2xl font-bold text-gray-900">Versionsvergleich</h1>

      {/* Version header cards */}
      <div className="grid grid-cols-2 gap-4">
        {[{ v: vA, label: 'Version A (Älter)', id: aId }, { v: vB, label: 'Version B (Neuer)', id: bId }].map(({ v, label, id }) => (
          <div key={id} className="bg-white border border-gray-200 rounded-xl p-4">
            <p className="text-xs text-gray-400 mb-1">{label}</p>
            {v ? (
              <>
                <p className="font-semibold text-gray-900">{v.file_name}</p>
                <p className="text-sm text-gray-500">v{v.version_number} · {v.uploader_username}</p>
                <p className="text-xs text-gray-400">{format(new Date(v.uploaded_at), 'dd. MMM yyyy', { locale: de })}</p>
                <a
                  href={versionsApi.downloadUrl(id)}
                  className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline mt-2"
                  download={v.file_name}
                >
                  <Download className="w-3 h-3" /> Herunterladen
                </a>
              </>
            ) : (
              <div className="text-gray-300 text-sm">Lade...</div>
            )}
          </div>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        {isLoading && <p className="text-gray-400 text-sm py-4 text-center">Vergleich wird berechnet...</p>}
        {error && <p className="text-red-500 text-sm">Vergleich fehlgeschlagen</p>}
        {comparison && <ComparisonViewer result={comparison} />}
      </div>
    </div>
  )
}
