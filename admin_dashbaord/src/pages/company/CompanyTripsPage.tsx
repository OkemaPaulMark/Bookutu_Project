import { FormEvent, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { listTripsRequest, createTripRequest, updateTripRequest, type TripRecord } from '@/lib/trips'
import { listRoutesRequest, listBusesRequest, listDriversRequest } from '@/lib/fleet'
import { getApiErrorMessage } from '@/lib/api'

const STATUS_COLORS: Record<string, string> = {
  SCHEDULED: 'bg-blue-100 text-blue-800',
  IN_PROGRESS: 'bg-emerald-100 text-emerald-800',
  COMPLETED: 'bg-slate-100 text-slate-800',
  CANCELLED: 'bg-rose-100 text-rose-800'
}

const emptyForm = { routeId: '', busId: '', driverId: '', departureDate: '', departureTime: '', arrivalTime: '', baseFare: 0, notes: '' }

export default function CompanyTripsPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [editingTrip, setEditingTrip] = useState<TripRecord | null>(null)
  const [form, setForm] = useState(emptyForm)

  const tripsQuery = useQuery({ queryKey: ['trips'], queryFn: () => listTripsRequest() })
  const routesQuery = useQuery({ queryKey: ['routes'], queryFn: listRoutesRequest })
  const busesQuery = useQuery({ queryKey: ['buses'], queryFn: listBusesRequest })
  const driversQuery = useQuery({ queryKey: ['drivers'], queryFn: listDriversRequest })

  const createMutation = useMutation({
    mutationFn: createTripRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['trips'] }); toast.success('Trip scheduled'); setShowModal(false); setForm(emptyForm) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to schedule trip'))
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateTripRequest>[1] }) => updateTripRequest(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['trips'] }); toast.success('Trip updated'); setShowModal(false); setEditingTrip(null) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to update trip'))
  })

  function openCreate() { setEditingTrip(null); setForm(emptyForm); setShowModal(true) }
  function openEdit(trip: TripRecord) {
    setEditingTrip(trip)
    setForm({ routeId: trip.routeId, busId: trip.busId, driverId: trip.driverId ?? '', departureDate: trip.departureDate.slice(0, 10), departureTime: trip.departureTime, arrivalTime: trip.arrivalTime, baseFare: Number(trip.baseFare), notes: trip.notes ?? '' })
    setShowModal(true)
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: name === 'baseFare' ? Number(value) : value }))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (editingTrip) {
      updateMutation.mutate({ id: editingTrip.id, payload: { departureDate: form.departureDate, departureTime: form.departureTime, arrivalTime: form.arrivalTime, baseFare: form.baseFare, driverId: form.driverId || undefined, notes: form.notes } })
    } else {
      createMutation.mutate({ ...form, driverId: form.driverId || undefined })
    }
  }

  const trips = tripsQuery.data ?? []
  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Trips</h1>
          <p className="mt-1 text-sm text-slate-600">Schedule and manage bus trips</p>
        </div>
        <button onClick={openCreate} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition">
          <Plus size={18} /> Schedule Trip
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="card p-4"><p className="text-sm text-slate-600">Total</p><p className="mt-2 text-2xl font-bold text-slate-900">{trips.length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Scheduled</p><p className="mt-2 text-2xl font-bold text-blue-600">{trips.filter(t => t.status === 'SCHEDULED').length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Completed</p><p className="mt-2 text-2xl font-bold text-emerald-600">{trips.filter(t => t.status === 'COMPLETED').length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Cancelled</p><p className="mt-2 text-2xl font-bold text-rose-600">{trips.filter(t => t.status === 'CANCELLED').length}</p></div>
      </div>

      {tripsQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading trips...</div>}
      {tripsQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(tripsQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Route', 'Bus', 'Driver', 'Date', 'Time', 'Fare', 'Seats', 'Status', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {trips.length === 0 && !tripsQuery.isLoading ? (
                <tr><td colSpan={9} className="px-6 py-8 text-center text-slate-500">No trips scheduled yet</td></tr>
              ) : trips.map(trip => (
                <tr key={trip.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 text-sm font-medium text-slate-900">{trip.route.originCity} → {trip.route.destinationCity}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{trip.bus.licensePlate}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{trip.driver ? `${trip.driver.firstName} ${trip.driver.lastName}` : '—'}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{new Date(trip.departureDate).toLocaleDateString()}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{trip.departureTime} → {trip.arrivalTime}</td>
                  <td className="px-6 py-3 text-sm font-semibold text-slate-900">UGX {Number(trip.baseFare).toLocaleString()}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{trip.bookedSeats}/{trip.availableSeats + trip.bookedSeats}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[trip.status] ?? 'bg-slate-100 text-slate-800'}`}>{trip.status}</span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    {trip.status === 'SCHEDULED' && (
                      <button onClick={() => openEdit(trip)} className="rounded px-2 py-1 text-xs font-medium text-amber-700 hover:bg-amber-50 transition">Edit</button>
                    )}
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
              <h2 className="text-xl font-semibold text-slate-900">{editingTrip ? 'Edit Trip' : 'Schedule Trip'}</h2>
              <button onClick={() => setShowModal(false)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4 p-6">
              {!editingTrip && (
                <>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Route</span>
                    <select name="routeId" value={form.routeId} onChange={handleChange} required className="input">
                      <option value="">Select route</option>
                      {(routesQuery.data ?? []).filter(r => r.isActive).map(r => (
                        <option key={r.id} value={r.id}>{r.name}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Bus</span>
                    <select name="busId" value={form.busId} onChange={handleChange} required className="input">
                      <option value="">Select bus</option>
                      {(busesQuery.data ?? []).filter(b => b.status === 'ACTIVE').map(b => (
                        <option key={b.id} value={b.id}>{b.licensePlate} — {b.make} {b.model}</option>
                      ))}
                    </select>
                  </label>
                </>
              )}
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Driver (optional)</span>
                <select name="driverId" value={form.driverId} onChange={handleChange} className="input">
                  <option value="">No driver assigned</option>
                  {(driversQuery.data ?? []).filter(d => d.status === 'ACTIVE').map(d => (
                    <option key={d.id} value={d.id}>{d.firstName} {d.lastName}</option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Departure Date</span>
                <input name="departureDate" type="date" value={form.departureDate} onChange={handleChange} required className="input" />
              </label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Departure Time</span><input name="departureTime" type="time" value={form.departureTime} onChange={handleChange} required className="input" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Arrival Time</span><input name="arrivalTime" type="time" value={form.arrivalTime} onChange={handleChange} required className="input" /></label>
              </div>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Base Fare (UGX)</span>
                <input name="baseFare" type="number" value={form.baseFare} onChange={handleChange} required className="input" min={1000} step={1000} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Notes (optional)</span>
                <input name="notes" value={form.notes} onChange={handleChange} className="input" placeholder="e.g. Morning express" />
              </label>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {isSubmitting && <Loader2 size={15} className="animate-spin" />}
                  {editingTrip ? 'Save Changes' : 'Schedule Trip'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}
