import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { useDashboardStats, useActivity } from '../hooks'
import { Building2, FolderOpen, FileText, Clock } from 'lucide-react'

export default function DashboardPage() {
  const { data: stats } = useDashboardStats()
  const { data: activity = [] } = useActivity()

  const statCards = [
    { label: 'Kunden', value: stats?.customers ?? '—', icon: Building2, color: 'text-blue-600 bg-blue-50' },
    { label: 'Projekte', value: stats?.projects ?? '—', icon: FolderOpen, color: 'text-green-600 bg-green-50' },
    { label: 'Dokumente', value: stats?.documents ?? '—', icon: FileText, color: 'text-purple-600 bg-purple-50' },
    { label: 'Versionen', value: stats?.versions ?? '—', icon: Clock, color: 'text-orange-600 bg-orange-50' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(card => (
          <div key={card.label} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className={`w-10 h-10 rounded-lg ${card.color} flex items-center justify-center mb-3`}>
              <card.icon className="w-5 h-5" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            <p className="text-sm text-gray-500">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">Letzte Aktivitäten</h2>
        </div>
        <div className="divide-y divide-gray-50">
          {activity.map(entry => (
            <div key={entry.id} className="px-4 py-3 flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium text-gray-600 shrink-0">
                {entry.username.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800">
                  <span className="font-medium">{entry.username}</span>
                  {' '}
                  {entry.action === 'upload' ? 'hat eine Datei hochgeladen' : entry.action}
                  {entry.metadata?.filename && (
                    <span className="text-gray-500"> — {entry.metadata.filename}</span>
                  )}
                  {entry.metadata?.version && (
                    <span className="text-gray-400"> (v{entry.metadata.version})</span>
                  )}
                </p>
                <p className="text-xs text-gray-400">
                  {format(new Date(entry.created_at), 'dd. MMM yyyy, HH:mm', { locale: de })}
                </p>
              </div>
            </div>
          ))}
          {activity.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-400 text-sm">Noch keine Aktivitäten</div>
          )}
        </div>
      </div>
    </div>
  )
}
