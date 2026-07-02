import { FormEvent, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { listDriversRequest, createDriverRequest, type DriverRecord } from '@/lib/fleet'
import { getApiErrorMessage } from '@/lib/api'

const emptyForm = {
  firstName: '', lastName: '', phoneNumber: '', email: '',
  licenseNumber: '', licenseExpiryDate: '', dateOfBirth: '', hireDate: '', employeeId: ''
}

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-800',
  INACTIVE: 'bg-amber-100 text-amber-800',
  SUSPENDED: 'bg-rose-100 text-rose-800'
}

export default function CompanyDriversPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const driversQuery = useQuery({ queryKey: ['drivers'], queryFn: listDriversRequest })

  const createMutation = useMutation({
    mutationFn: createDriverRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['drivers'] }); toast.success('Driver registered'); setShowModal(false); setForm(emptyForm) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to register driver'))
  })

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    createMutation.mutate(form)
  }

  const drivers = driversQuery.data ?? []

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Drivers</h1>
          <p className="mt-1 text-sm text-slate-600">Manage your company drivers</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition">
          <Plus size={18} /> Register Driver
        </button>
      </div>

      {driversQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading drivers...</div>}
      {driversQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(driversQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Name', 'Phone', 'Email', 'License No.', 'License Expiry', 'Hire Date', 'Status'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {drivers.length === 0 && !driversQuery.isLoading ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">No drivers registered yet</td></tr>
              ) : drivers.map((driver: DriverRecord) => (
                <tr key={driver.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 text-sm font-medium text-slate-900">{driver.firstName} {driver.lastName}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{driver.phoneNumber}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{driver.email ?? '—'}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{driver.licenseNumber}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{new Date(driver.licenseExpiryDate).toLocaleDateString()}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{new Date(driver.hireDate).toLocaleDateString()}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[driver.status] ?? 'bg-slate-100 text-slate-800'}`}>{driver.status}</span>
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
              <h2 className="text-xl font-semibold text-slate-900">Register Driver</h2>
              <button onClick={() => setShowModal(false)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4 p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">First Name</span><input name="firstName" value={form.firstName} onChange={handleChange} required className="input" placeholder="Moses" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Last Name</span><input name="lastName" value={form.lastName} onChange={handleChange} required className="input" placeholder="Okello" /></label>
              </div>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Phone Number</span><input name="phoneNumber" value={form.phoneNumber} onChange={handleChange} required className="input" placeholder="+256701000000" /></label>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Email (optional)</span><input name="email" type="email" value={form.email} onChange={handleChange} className="input" placeholder="driver@example.com" /></label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">License Number</span><input name="licenseNumber" value={form.licenseNumber} onChange={handleChange} required className="input" placeholder="DL-2024-001" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">License Expiry</span><input name="licenseExpiryDate" type="date" value={form.licenseExpiryDate} onChange={handleChange} required className="input" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Date of Birth</span><input name="dateOfBirth" type="date" value={form.dateOfBirth} onChange={handleChange} required className="input" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Hire Date</span><input name="hireDate" type="date" value={form.hireDate} onChange={handleChange} required className="input" /></label>
              </div>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Employee ID (optional)</span><input name="employeeId" value={form.employeeId} onChange={handleChange} className="input" placeholder="EMP-001" /></label>
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
    </section>
  )
}
