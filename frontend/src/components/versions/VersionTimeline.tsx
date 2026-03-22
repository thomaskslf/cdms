import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { Download, GitCompare, Star, User } from 'lucide-react'
import type { DocumentVersion } from '../../types'
import { versionsApi } from '../../api'

interface Props {
  versions: DocumentVersion[]
  documentId?: number
}

export default function VersionTimeline({ versions }: Props) {
  const [compareA, setCompareA] = useState<number | null>(null)
  const navigate = useNavigate()

  const handleCompare = (versionId: number) => {
    if (!compareA) {
      setCompareA(versionId)
    } else {
      navigate(`/compare/${compareA}/${versionId}`)
      setCompareA(null)
    }
  }

  return (
    <div className="relative">
      {compareA && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          Version ausgewählt — klicke auf eine zweite Version zum Vergleichen
          <button onClick={() => setCompareA(null)} className="ml-2 text-blue-500 hover:text-blue-700">✕</button>
        </div>
      )}

      <div className="relative pl-6">
        {/* Vertical line */}
        <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gray-200" />

        {versions.map((version) => (
          <div key={version.id} className="relative mb-4 last:mb-0">
            {/* Dot */}
            <div className={`absolute -left-4 top-3 w-3 h-3 rounded-full border-2 ${
              version.is_current
                ? 'bg-blue-500 border-blue-500'
                : 'bg-white border-gray-300'
            }`} />

            <div className={`bg-white border rounded-xl p-4 ml-2 ${
              version.is_current ? 'border-blue-200 shadow-sm' : 'border-gray-200'
            }`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900 text-sm">v{version.version_number}</span>
                    {version.version_label && (
                      <span className="text-xs text-gray-500">{version.version_label}</span>
                    )}
                    {version.is_current && (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                        <Star className="w-3 h-3" /> Aktuell
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {version.uploader_username || 'Unbekannt'}
                    </span>
                    <span>{format(new Date(version.uploaded_at), 'dd. MMM yyyy, HH:mm', { locale: de })}</span>
                    <span>{(version.file_size / 1024).toFixed(0)} KB</span>
                  </div>

                  {version.change_summary && (
                    <p className="mt-1.5 text-xs text-gray-600 italic">{version.change_summary}</p>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleCompare(version.id)}
                    className={`flex items-center gap-1 text-xs px-2 py-1 rounded border transition-colors ${
                      compareA === version.id
                        ? 'bg-blue-100 border-blue-400 text-blue-700'
                        : 'border-gray-200 text-gray-600 hover:border-blue-300 hover:text-blue-600'
                    }`}
                    title="Version vergleichen"
                  >
                    <GitCompare className="w-3 h-3" />
                    {compareA === version.id ? 'Ausgewählt' : 'Vergleichen'}
                  </button>
                  <a
                    href={versionsApi.downloadUrl(version.id)}
                    className="flex items-center gap-1 text-xs px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-gray-400"
                    download={version.file_name}
                  >
                    <Download className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
