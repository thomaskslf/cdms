import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCustomers, useProjects, useCreateCustomer, useCreateProject } from '../../hooks'
import { ChevronRight, ChevronDown, Plus, Folder, Building2 } from 'lucide-react'

export default function Sidebar() {
  const [expandedCustomers, setExpandedCustomers] = useState<Set<number>>(new Set())
  const [showNewCustomer, setShowNewCustomer] = useState(false)
  const [showNewProject, setShowNewProject] = useState<number | null>(null)
  const [newCustomerName, setNewCustomerName] = useState('')
  const [newProjectName, setNewProjectName] = useState('')

  const { data: customers = [] } = useCustomers()
  const createCustomer = useCreateCustomer()
  const createProject = useCreateProject()
  const navigate = useNavigate()

  const toggleCustomer = (id: number) => {
    setExpandedCustomers(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleCreateCustomer = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newCustomerName.trim()) return
    const customer = await createCustomer.mutateAsync(newCustomerName.trim())
    setNewCustomerName('')
    setShowNewCustomer(false)
    setExpandedCustomers(prev => new Set([...prev, customer.id]))
  }

  const handleCreateProject = async (e: React.FormEvent, customerId: number) => {
    e.preventDefault()
    if (!newProjectName.trim()) return
    const project = await createProject.mutateAsync({ customerId, name: newProjectName.trim() })
    setNewProjectName('')
    setShowNewProject(null)
    navigate(`/projects/${project.id}`)
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col overflow-y-auto">
      <div className="p-4 border-b border-gray-100">
        <Link to="/" className="text-sm font-medium text-gray-700 hover:text-blue-600">Dashboard</Link>
      </div>

      <div className="flex-1 p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Kunden</span>
          <button onClick={() => setShowNewCustomer(v => !v)} className="text-gray-400 hover:text-blue-600">
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        {showNewCustomer && (
          <form onSubmit={handleCreateCustomer} className="mb-2 flex gap-1">
            <input
              autoFocus
              type="text"
              value={newCustomerName}
              onChange={e => setNewCustomerName(e.target.value)}
              placeholder="Kundenname"
              className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button type="submit" className="text-xs bg-blue-600 text-white px-2 rounded">+</button>
          </form>
        )}

        {customers.map(customer => (
          <CustomerItem
            key={customer.id}
            customer={customer}
            expanded={expandedCustomers.has(customer.id)}
            onToggle={() => toggleCustomer(customer.id)}
            showNewProject={showNewProject === customer.id}
            onNewProject={() => setShowNewProject(showNewProject === customer.id ? null : customer.id)}
            newProjectName={newProjectName}
            onProjectNameChange={setNewProjectName}
            onCreateProject={(e) => handleCreateProject(e, customer.id)}
          />
        ))}
      </div>
    </aside>
  )
}

function CustomerItem({ customer, expanded, onToggle, showNewProject, onNewProject, newProjectName, onProjectNameChange, onCreateProject }: {
  customer: { id: number; name: string }
  expanded: boolean
  onToggle: () => void
  showNewProject: boolean
  onNewProject: () => void
  newProjectName: string
  onProjectNameChange: (v: string) => void
  onCreateProject: (e: React.FormEvent) => void
}) {
  const { data: projects = [] } = useProjects(expanded ? customer.id : null)

  return (
    <div className="mb-1">
      <div
        className="flex items-center gap-1.5 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-50 group"
        onClick={onToggle}
      >
        {expanded ? <ChevronDown className="w-3 h-3 text-gray-400" /> : <ChevronRight className="w-3 h-3 text-gray-400" />}
        <Building2 className="w-3.5 h-3.5 text-gray-500" />
        <span className="flex-1 text-sm text-gray-700 truncate">{customer.name}</span>
        <button
          onClick={e => { e.stopPropagation(); onNewProject() }}
          className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-blue-600"
        >
          <Plus className="w-3 h-3" />
        </button>
      </div>

      {expanded && (
        <div className="ml-4">
          {showNewProject && (
            <form onSubmit={onCreateProject} className="flex gap-1 mb-1">
              <input
                autoFocus
                type="text"
                value={newProjectName}
                onChange={e => onProjectNameChange(e.target.value)}
                placeholder="Projektname"
                className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button type="submit" className="text-xs bg-blue-600 text-white px-2 rounded">+</button>
            </form>
          )}
          {projects.map(project => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-gray-50 text-sm text-gray-600 hover:text-gray-900"
            >
              <Folder className="w-3.5 h-3.5 text-gray-400" />
              <span className="truncate">{project.name}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
