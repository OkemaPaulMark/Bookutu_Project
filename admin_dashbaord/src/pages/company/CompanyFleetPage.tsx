import { FormEvent, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { listBusesRequest, createBusRequest, updateBusRequest, type BusRecord } from '@/lib/fleet'
import { getApiErrorMessage } from '@/lib/api'

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-800',
  MAINTENANCE: 'bg-amber-100 text-amber-800',
  INACTIVE: 'bg-rose-100 text-rose-800'
}

const emptyForm = {
  licensePlate: '', model: '', make: '', year: new Date().getFullYear(),
  totalSeats: 32, busType: 'MINIBUS', hasAc: true, hasWifi: false, hasChargingPorts: false
}

export default function CompanyFleetPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [editingBus, setEditingBus] = useState<BusRecord | null>(null)
  const [form, setForm] = useState(emptyForm)

  const busesQuery = useQuery({ queryKey: ['buses'], queryFn: listBusesRequest })

  const createMutation = useMutation({
    mutationFn: createBusRequest,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['buses'] })
      toast.success('Bus added to fleet')
      setShowModal(false)
      setForm(emptyForm)
    },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to add bus'))
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateBusRequest>[1] }) =>
      updateBusRequest(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['buses'] })
      toast.success('Bus updated')
      setShowModal(false)
      setEditingBus(null)
    },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to update bus'))
  })

  function openCreate() { setEditingBus(null); setForm(emptyForm); setShowModal(true) }
  function openEdit(bus: BusRecord) {
    setEditingBus(bus)
    setForm({ licensePlate: bus.licensePlate, model: bus.model, make: bus.make, year: bus.year, totalSeats: bus.totalSeats, busType: bus.busType, hasAc: bus.hasAc, hasWifi: bus.hasWifi, hasChargingPorts: bus.hasChargingPorts })
    setShowModal(true)
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value, type } = e.target
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : ['year', 'totalSeats'].includes(name) ? Number(value) : value }))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (editingBus) {
      updateMutation.mutate({ id: editingBus.id, payload: { model: form.model, make: form.make, year: form.year, busType: form.busType, hasAc: form.hasAc, hasWifi: form.hasWifi, hasChargingPorts: form.hasChargingPorts } })
    } else {
      createMutation.mutate(form)
    }
  }

  const buses = busesQuery.data ?? []
  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Fleet</h1>
          <p className="mt-1 text-sm text-slate-600">Manage your company buses</p>
        </div>
        <button onClick={openCreate} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition">
          <Plus size={18} /> Add Bus
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-4"><p className="text-sm text-slate-600">Total Buses</p><p className="mt-2 text-2xl font-bold text-slate-900">{buses.length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Active</p><p className="mt-2 text-2xl font-bold text-emerald-600">{buses.filter(b => b.status === 'ACTIVE').length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Total Seats</p><p className="mt-2 text-2xl font-bold text-slate-900">{buses.reduce((s, b) => s + b.totalSeats, 0)}</p></div>
      </div>

      {busesQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading fleet...</div>}
      {busesQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(busesQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['License Plate', 'Make / Model', 'Year', 'Seats', 'Type', 'Status', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {buses.length === 0 && !busesQuery.isLoading ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">No buses in fleet yet</td></tr>
              ) : buses.map(bus => (
                <tr key={bus.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 text-sm font-medium text-blue-600">{bus.licensePlate}</td>
                  <td className="px-6 py-3 text-sm text-slate-900">{bus.make} {bus.model}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{bus.year}</td>
                  <td className="px-6 py-3 text-sm text-slate-900">{bus.totalSeats}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{bus.busType}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[bus.status] ?? 'bg-slate-100 text-slate-800'}`}>{bus.status}</span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <button onClick={() => openEdit(bus)} className="rounded px-2 py-1 text-xs font-medium text-amber-700 hover:bg-amber-50 transition">Edit</button>
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
              <h2 className="text-xl font-semibold text-slate-900">{editingBus ? 'Edit Bus' : 'Add Bus'}</h2>
              <button onClick={() => setShowModal(false)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4 p-6">
              {!editingBus && (
                <label className="block">
                  <span className="mb-1 block text-sm font-medium text-slate-700">License Plate</span>
                  <input name="licensePlate" value={form.licensePlate} onChange={handleChange} required className="input" placeholder="UAA 123B" />
                </label>
              )}
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-1 block text-sm font-medium text-slate-700">Make</span>
                  <input name="make" value={form.make} onChange={handleChange} required className="input" placeholder="Toyota" />
                </label>
                <label className="block">
                  <span className="mb-1 block text-sm font-medium text-slate-700">Model</span>
                  <input name="model" value={form.model} onChange={handleChange} required className="input" placeholder="Coaster" />
                </label>
                <label className="block">
                  <span className="mb-1 block text-sm font-medium text-slate-700">Year</span>
                  <input name="year" type="number" value={form.year} onChange={handleChange} required className="input" min={2000} max={new Date().getFullYear()} />
                </label>
                {!editingBus && (
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Total Seats</span>
                    <input name="totalSeats" type="number" value={form.totalSeats} onChange={handleChange} required className="input" min={4} max={100} />
                  </label>
                )}
              </div>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Bus Type</span>
                <select name="busType" value={form.busType} onChange={handleChange} className="input">
                  <option value="MINIBUS">Minibus</option>
                  <option value="COACH">Coach</option>
                  <option value="LUXURY">Luxury</option>
                </select>
              </label>
              <div className="flex gap-6">
                {(['hasAc', 'hasWifi', 'hasChargingPorts'] as const).map(key => (
                  <label key={key} className="flex items-center gap-2 text-sm text-slate-700">
                    <input type="checkbox" name={key} checked={form[key] as boolean} onChange={handleChange} />
                    {key === 'hasAc' ? 'AC' : key === 'hasWifi' ? 'WiFi' : 'Charging'}
                  </label>
                ))}
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {isSubmitting && <Loader2 size={15} className="animate-spin" />}
                  {editingBus ? 'Save Changes' : 'Add Bus'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}
