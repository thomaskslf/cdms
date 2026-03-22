import type { DocType } from '../../types'
import { DOC_TYPE_LABELS, DOC_TYPE_COLORS } from '../../types'

export default function CategoryBadge({ docType }: { docType: DocType }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${DOC_TYPE_COLORS[docType]}`}>
      {DOC_TYPE_LABELS[docType]}
    </span>
  )
}
