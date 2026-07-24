import { FormEvent, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, AlertCircle, Filter, CheckCircle2, Copy, Pencil, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import {
  listDeliveriesRequest,
  createDeliveryRequest,
  updateDeliveryStatusRequest,
  deleteDeliveryRequest,
  type DeliveryRecord,
  type DeliveryStatus
} from '@/lib/deliveries'
import { getApiErrorMessage } from '@/lib/api'

function nowForDatetimeLocal() {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
}

const emptyForm = {
  sentAt: '', senderName: '', senderPhone: '', receiverName: '', receiverPhone: '',
  originTerminal: '', destinationTerminal: '', packageDescription: '', fee: ''
}

const STATUS_COLORS: Record<string, string> = {
  REGISTERED: 'bg-amber-100 text-amber-800',
  ON_DELIVERY: 'bg-blue-100 text-blue-800',
  PICKED_UP: 'bg-emerald-100 text-emerald-800',
  CANCELLED: 'bg-rose-100 text-rose-800'
}

const NEXT_STATUSES: Record<DeliveryStatus, DeliveryStatus[]> = {
  REGISTERED: ['ON_DELIVERY', 'PICKED_UP', 'CANCELLED'],
  ON_DELIVERY: ['PICKED_UP', 'CANCELLED'],
  PICKED_UP: [],
  CANCELLED: []
}

export default function CompanyDeliveriesPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [statusFilter, setStatusFilter] = useState<DeliveryStatus | ''>('')
  const [search, setSearch] = useState('')
  const [justRegistered, setJustRegistered] = useState<DeliveryRecord | null>(null)
  const [editingDelivery, setEditingDelivery] = useState<DeliveryRecord | null>(null)
  const [statusForm, setStatusForm] = useState<DeliveryStatus | ''>('')

  const deliveriesQuery = useQuery({
    queryKey: ['deliveries', statusFilter, search],
    queryFn: () => listDeliveriesRequest({ status: statusFilter || undefined, search: search || undefined })
  })

  const createMutation = useMutation({
    mutationFn: createDeliveryRequest,
    onSuccess: (delivery) => {
      qc.invalidateQueries({ queryKey: ['deliveries'] })
      toast.success(`Package registered — tracking number ${delivery.trackingNumber}`)
      setShowModal(false)
      setForm(emptyForm)
      setJustRegistered(delivery)
    },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to register package'))
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status: newStatus }: { id: string; status: DeliveryStatus }) => updateDeliveryStatusRequest(id, newStatus),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['deliveries'] }); toast.success('Delivery status updated'); setEditingDelivery(null) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to update status'))
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDeliveryRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['deliveries'] }); toast.success('Delivery deleted') },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to delete delivery'))
  })

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    createMutation.mutate({ ...form, fee: Number(form.fee) })
  }

  function copyTrackingNumber(trackingNumber: string) {
    navigator.clipboard.writeText(trackingNumber)
    toast.success('Tracking number copied')
  }

  function openEditStatus(delivery: DeliveryRecord) {
    setEditingDelivery(delivery)
    setStatusForm('')
  }

  function handleStatusSubmit(e: FormEvent) {
    e.preventDefault()
    if (!editingDelivery || !statusForm) return
    if (window.confirm(`Are you sure you want to change this delivery's status to "${statusForm.replace('_', ' ')}"?`)) {
      statusMutation.mutate({ id: editingDelivery.id, status: statusForm })
    }
  }

  function handleDelete(delivery: DeliveryRecord) {
    if (window.confirm(`Delete delivery ${delivery.trackingNumber}? This cannot be undone.`)) {
      deleteMutation.mutate(delivery.id)
    }
  }

  const deliveries = deliveriesQuery.data ?? []

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Deliveries</h1>
          <p className="mt-1 text-sm text-slate-600">Register sent packages and check them in on pickup</p>
        </div>
        <button onClick={() => { setForm({ ...emptyForm, sentAt: nowForDatetimeLocal() }); setShowModal(true) }} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition">
          <Plus size={18} /> Register Package
        </button>
      </div>

      {justRegistered && (
        <div className="card flex items-center justify-between border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-center gap-3">
            <CheckCircle2 size={20} className="text-emerald-600" />
            <div>
              <p className="text-sm text-emerald-800">Package registered. Give this tracking number to the sender:</p>
              <p className="mt-1 font-mono text-lg font-bold text-emerald-900">{justRegistered.trackingNumber}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => copyTrackingNumber(justRegistered.trackingNumber)} className="flex items-center gap-1 rounded-lg border border-emerald-300 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-100 transition">
              <Copy size={14} /> Copy
            </button>
            <button onClick={() => setJustRegistered(null)}><X size={18} className="text-emerald-700" /></button>
          </div>
        </div>
      )}

      <div className="card flex flex-wrap items-center gap-4 p-4">
        <Filter size={18} className="text-slate-500" />
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as DeliveryStatus | '')} className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500">
          <option value="">All Statuses</option>
          {(['REGISTERED', 'ON_DELIVERY', 'PICKED_UP', 'CANCELLED'] as DeliveryStatus[]).map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by tracking no., sender, receiver..." className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 w-72" />
        {deliveriesQuery.isFetching && <Loader2 size={16} className="animate-spin text-slate-400" />}
      </div>

      {deliveriesQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading deliveries...</div>}
      {deliveriesQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(deliveriesQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Tracking No.', 'Sender', 'Receiver', 'Route', 'Fee', 'Status', 'Date', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {deliveries.length === 0 && !deliveriesQuery.isLoading ? (
                <tr><td colSpan={8} className="px-6 py-8 text-center text-slate-500">No deliveries registered yet</td></tr>
              ) : deliveries.map((delivery: DeliveryRecord) => (
                <tr key={delivery.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 font-mono text-sm font-semibold text-blue-600">{delivery.trackingNumber}</td>
                  <td className="px-6 py-3 text-sm">
                    <p className="font-medium text-slate-900">{delivery.senderName}</p>
                    <p className="text-xs text-slate-500">{delivery.senderPhone}</p>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <p className="font-medium text-slate-900">{delivery.receiverName}</p>
                    <p className="text-xs text-slate-500">{delivery.receiverPhone}</p>
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-600">{delivery.originTerminal} → {delivery.destinationTerminal}</td>
                  <td className="px-6 py-3 text-sm font-semibold text-slate-900">UGX {Number(delivery.fee).toLocaleString()}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[delivery.status] ?? 'bg-slate-100 text-slate-800'}`}>{delivery.status.replace('_', ' ')}</span>
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-600">
                    {new Date(delivery.sentAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}, {new Date(delivery.sentAt).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <div className="flex items-center gap-1">
                      {NEXT_STATUSES[delivery.status].length > 0 && (
                        <button onClick={() => openEditStatus(delivery)} title="Edit status" className="rounded p-1.5 text-amber-700 hover:bg-amber-50 transition">
                          <Pencil size={15} />
                        </button>
                      )}
                      <button onClick={() => handleDelete(delivery)} disabled={deleteMutation.isPending} title="Delete" className="rounded p-1.5 text-rose-700 hover:bg-rose-50 transition disabled:opacity-50">
                        <Trash2 size={15} />
                      </button>
                    </div>
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
              <h2 className="text-xl font-semibold text-slate-900">Register Package</h2>
              <button onClick={() => setShowModal(false)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4 p-6">
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Sending Date & Time</span><input name="sentAt" type="datetime-local" value={form.sentAt} onChange={handleChange} required className="input" /></label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Sender Name</span><input name="senderName" value={form.senderName} onChange={handleChange} required className="input" placeholder="Moses Okello" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Sender Phone</span><input name="senderPhone" value={form.senderPhone} onChange={handleChange} required className="input" placeholder="+256701000000" /></label>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Receiver Name</span><input name="receiverName" value={form.receiverName} onChange={handleChange} required className="input" placeholder="Jane Doe" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Receiver Phone</span><input name="receiverPhone" value={form.receiverPhone} onChange={handleChange} required className="input" placeholder="+256702000000" /></label>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Origin Terminal</span><input name="originTerminal" value={form.originTerminal} onChange={handleChange} required className="input" placeholder="Kampala" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Destination Terminal</span><input name="destinationTerminal" value={form.destinationTerminal} onChange={handleChange} required className="input" placeholder="Gulu" /></label>
              </div>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Package Description</span><textarea name="packageDescription" value={form.packageDescription} onChange={handleChange} required rows={2} className="input" placeholder="Small box, documents, etc." /></label>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Fee (UGX)</span><input name="fee" type="number" min="0" step="0.01" value={form.fee} onChange={handleChange} required className="input" placeholder="5000" /></label>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={createMutation.isPending} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {createMutation.isPending && <Loader2 size={15} className="animate-spin" />}
                  Register
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editingDelivery && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card w-full max-w-sm overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900">Update Status</h2>
              <button onClick={() => setEditingDelivery(null)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleStatusSubmit} className="space-y-4 p-6">
              <p className="text-sm text-slate-600">
                Tracking number <span className="font-mono font-semibold text-slate-900">{editingDelivery.trackingNumber}</span> — currently <span className="font-semibold">{editingDelivery.status.replace('_', ' ')}</span>
              </p>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">New Status</span>
                <select value={statusForm} onChange={e => setStatusForm(e.target.value as DeliveryStatus)} required className="input">
                  <option value="">Select new status</option>
                  {NEXT_STATUSES[editingDelivery.status].map(s => (
                    <option key={s} value={s}>{s.replace('_', ' ')}</option>
                  ))}
                </select>
              </label>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setEditingDelivery(null)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={statusMutation.isPending || !statusForm} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {statusMutation.isPending && <Loader2 size={15} className="animate-spin" />}
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}
