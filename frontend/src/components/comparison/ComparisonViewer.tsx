import type { ComparisonResult } from '../../types'
import BomDiffViewer from './BomDiffViewer'
import TextDiffViewer from './TextDiffViewer'
import DxfDiffViewer from './DxfDiffViewer'

export default function ComparisonViewer({ result }: { result: ComparisonResult }) {
  const { comparison_type, diff_data, summary } = result

  return (
    <div>
      <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm font-medium text-gray-800">{summary}</p>
        <p className="text-xs text-gray-400 mt-0.5">Vergleichsmethode: {comparison_type.toUpperCase()}</p>
      </div>
      {comparison_type === 'bom' && <BomDiffViewer diffData={diff_data as any} summary={summary} />}
      {comparison_type === 'text' && <TextDiffViewer diffData={diff_data as any} summary={summary} />}
      {comparison_type === 'dxf' && <DxfDiffViewer diffData={diff_data as any} summary={summary} />}
    </div>
  )
}
