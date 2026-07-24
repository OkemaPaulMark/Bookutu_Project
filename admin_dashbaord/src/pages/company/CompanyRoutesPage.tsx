import { FormEvent, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { listRoutesRequest, createRouteRequest, updateRouteRequest, type RouteRecord } from '@/lib/fleet'
import { getApiErrorMessage } from '@/lib/api'

const emptyForm = {
  name: '', originCity: '', originTerminal: '', destinationCity: '',
  destinationTerminal: '', distanceKm: 0, estimatedDurationHours: 1, baseFare: 0
}

export default function CompanyRoutesPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [editingRoute, setEditingRoute] = useState<RouteRecord | null>(null)
  const [form, setForm] = useState(emptyForm)

  const routesQuery = useQuery({ queryKey: ['routes'], queryFn: listRoutesRequest })

  const createMutation = useMutation({
    mutationFn: createRouteRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['routes'] }); toast.success('Route created'); setShowModal(false); setForm(emptyForm) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to create route'))
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateRouteRequest>[1] }) => updateRouteRequest(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['routes'] }); toast.success('Route updated'); setShowModal(false); setEditingRoute(null) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to update route'))
  })

  function openCreate() { setEditingRoute(null); setForm(emptyForm); setShowModal(true) }
  function openEdit(route: RouteRecord) {
    setEditingRoute(route)
    setForm({ name: route.name, originCity: route.originCity, originTerminal: route.originTerminal, destinationCity: route.destinationCity, destinationTerminal: route.destinationTerminal, distanceKm: route.distanceKm, estimatedDurationHours: Number(route.estimatedDurationHours), baseFare: Number(route.baseFare) })
    setShowModal(true)
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: ['distanceKm', 'estimatedDurationHours', 'baseFare'].includes(name) ? Number(value) : value }))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (editingRoute) {
      updateMutation.mutate({ id: editingRoute.id, payload: { name: form.name, baseFare: form.baseFare } })
    } else {
      createMutation.mutate(form)
    }
  }

  const routes = routesQuery.data ?? []
  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Routes</h1>
          <p className="mt-1 text-sm text-slate-600">Define and manage transport routes</p>
        </div>
        <button onClick={openCreate} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition">
          <Plus size={18} /> Create Route
        </button>
      </div>

      {routesQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading routes...</div>}
      {routesQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(routesQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Route', 'Origin', 'Destination', 'Distance', 'Duration', 'Base Fare', 'Status', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {routes.length === 0 && !routesQuery.isLoading ? (
                <tr><td colSpan={8} className="px-6 py-8 text-center text-slate-500">No routes created yet</td></tr>
              ) : routes.map(route => (
                <tr key={route.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 text-sm font-medium text-blue-600">{route.name}</td>
                  <td className="px-6 py-3 text-sm text-slate-900">{route.originCity}<p className="text-xs text-slate-400">{route.originTerminal}</p></td>
                  <td className="px-6 py-3 text-sm text-slate-900">{route.destinationCity}<p className="text-xs text-slate-400">{route.destinationTerminal}</p></td>
                  <td className="px-6 py-3 text-sm text-slate-600">{route.distanceKm} km</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{Number(route.estimatedDurationHours)}h</td>
                  <td className="px-6 py-3 text-sm font-semibold text-slate-900">UGX {Number(route.baseFare).toLocaleString()}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${route.isActive ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'}`}>{route.isActive ? 'Active' : 'Inactive'}</span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <button onClick={() => openEdit(route)} className="rounded px-2 py-1 text-xs font-medium text-amber-700 hover:bg-amber-50 transition">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card max-h-[90vh] w-full max-w-md overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900">{editingRoute ? 'Edit Route' : 'Create Route'}</h2>
              <button onClick={() => setShowModal(false)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4 p-6">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Route Name</span>
                <input name="name" value={form.name} onChange={handleChange} required className="input" placeholder="Kampala - Gulu Express" />
              </label>
              {!editingRoute && (
                <div className="grid gap-4 md:grid-cols-2">
                  <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Origin City</span><input name="originCity" value={form.originCity} onChange={handleChange} required className="input" placeholder="Kampala" /></label>
                  <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Origin Terminal</span><input name="originTerminal" value={form.originTerminal} onChange={handleChange} required className="input" placeholder="Kampala Coach Terminal" /></label>
                  <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Destination City</span><input name="destinationCity" value={form.destinationCity} onChange={handleChange} required className="input" placeholder="Gulu" /></label>
                  <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Destination Terminal</span><input name="destinationTerminal" value={form.destinationTerminal} onChange={handleChange} required className="input" placeholder="Gulu Bus Park" /></label>
                  <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Distance (km)</span><input name="distanceKm" type="number" value={form.distanceKm} onChange={handleChange} required className="input" min={1} /></label>
                  <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Duration (hours)</span><input name="estimatedDurationHours" type="number" value={form.estimatedDurationHours} onChange={handleChange} required className="input" min={0.5} step={0.5} /></label>
                </div>
              )}
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Base Fare (UGX)</span>
                <input name="baseFare" type="number" value={form.baseFare} onChange={handleChange} required className="input" min={1000} step={1000} />
              </label>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {isSubmitting && <Loader2 size={15} className="animate-spin" />}
                  {editingRoute ? 'Save Changes' : 'Create Route'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}
