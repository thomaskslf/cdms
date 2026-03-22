interface DxfDiff {
  entity_changes: Record<string, { old: number; new: number; delta: number }>
  header_changes: Record<string, { old: string; new: string }>
  added_layers: string[]
  removed_layers: string[]
}

export default function DxfDiffViewer({ diffData }: { diffData: DxfDiff; summary?: string }) {
  const hasChanges = Object.keys(diffData.entity_changes || {}).length > 0
    || Object.keys(diffData.header_changes || {}).length > 0
    || (diffData.added_layers?.length || 0) > 0
    || (diffData.removed_layers?.length || 0) > 0

  if (!hasChanges) {
    return <div className="py-8 text-center text-gray-400 text-sm">Keine DXF-Änderungen gefunden</div>
  }

  return (
    <div className="space-y-4">
      {Object.keys(diffData.entity_changes || {}).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Entitätsänderungen</h4>
          <table className="w-full text-xs border border-gray-200 rounded-lg overflow-hidden">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left">Typ</th>
                <th className="px-3 py-2 text-right">Vorher</th>
                <th className="px-3 py-2 text-right">Nachher</th>
                <th className="px-3 py-2 text-right">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {Object.entries(diffData.entity_changes).map(([type, change]) => (
                <tr key={type} className="hover:bg-gray-50">
                  <td className="px-3 py-2 font-mono text-gray-700">{type}</td>
                  <td className="px-3 py-2 text-right text-gray-600">{change.old}</td>
                  <td className="px-3 py-2 text-right text-gray-800 font-medium">{change.new}</td>
                  <td className={`px-3 py-2 text-right font-medium ${change.delta > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {change.delta > 0 ? '+' : ''}{change.delta}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(diffData.added_layers?.length > 0 || diffData.removed_layers?.length > 0) && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Layer-Änderungen</h4>
          <div className="flex gap-4 flex-wrap">
            {diffData.added_layers?.map(l => (
              <span key={l} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">+{l}</span>
            ))}
            {diffData.removed_layers?.map(l => (
              <span key={l} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">-{l}</span>
            ))}
          </div>
        </div>
      )}

      {Object.keys(diffData.header_changes || {}).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Header-Änderungen</h4>
          <div className="space-y-1">
            {Object.entries(diffData.header_changes).map(([key, change]) => (
              <div key={key} className="flex items-center gap-2 text-xs">
                <span className="font-mono text-gray-600 w-32 shrink-0">{key}</span>
                <span className="text-red-500 line-through">{change.old}</span>
                <span className="text-gray-400">→</span>
                <span className="text-green-600 font-medium">{change.new}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
