import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, Building2, Loader2, Pencil, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import Modal from '@components/Modal'
import { getApiErrorMessage } from '@/lib/api'
import {
  CompanyRecord,
  createCompanyRequest,
  deleteCompanyRequest,
  inviteCompanyAdminRequest,
  listCompaniesRequest,
  updateCompanyRequest,
} from '@/lib/companies'

type EditableFields = {
  name: string
  email: string
  phoneNumber: string
  city: string
  state: string
  status: CompanyRecord['status']
  commissionRate: number
}

type RegisterFields = {
  companyName: string
  registrationNumber: string
  adminEmail: string
  adminFirstName: string
  adminLastName: string
  adminPhoneNumber: string
}

const emptyRegisterForm: RegisterFields = {
  companyName: '',
  registrationNumber: '',
  adminEmail: '',
  adminFirstName: '',
  adminLastName: '',
  adminPhoneNumber: '',
}

function buildPlaceholderCompanyPayload(form: RegisterFields) {
  const timestamp = Date.now()
  return {
    name: form.companyName,
    email: `pending-${timestamp}@bookutu.local`,
    phoneNumber: form.adminPhoneNumber || '+256000000000',
    address: `${form.companyName} - details pending`,
    city: 'Pending',
    state: 'Pending',
    registrationNumber: form.registrationNumber || `PENDING-${timestamp}`,
    licenseNumber: `PENDING-${timestamp}`,
    description: 'Company details will be completed by the company admin.',
    website: undefined,
    postalCode: undefined,
    taxId: undefined,
    commissionRate: undefined,
  }
}

function RegisterCompanyForm({
  submitting,
  onSubmit,
}: {
  submitting: boolean
  onSubmit: (payload: RegisterFields) => void
}) {
  const [form, setForm] = useState<RegisterFields>(emptyRegisterForm)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(form)
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Company name</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, companyName: e.target.value }))}
          placeholder="Acme Coaches Ltd"
          required
          type="text"
          value={form.companyName}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Registration number</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, registrationNumber: e.target.value }))}
          placeholder="REG-123456"
          required
          type="text"
          value={form.registrationNumber}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Admin email</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, adminEmail: e.target.value }))}
          placeholder="manager@acmecoaches.com"
          required
          type="email"
          value={form.adminEmail}
        />
      </label>

      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">First name</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, adminFirstName: e.target.value }))}
            type="text"
            value={form.adminFirstName}
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Last name</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, adminLastName: e.target.value }))}
            type="text"
            value={form.adminLastName}
          />
        </label>
      </div>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Phone number</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, adminPhoneNumber: e.target.value }))}
          placeholder="+256..."
          type="text"
          value={form.adminPhoneNumber}
        />
      </label>

      <button
        className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-teal-300"
        disabled={submitting}
        type="submit"
      >
        {submitting ? <Loader2 className="animate-spin" size={18} /> : null}
        Create company and send invite
      </button>
    </form>
  )
}

function EditCompanyForm({
  company,
  submitting,
  onSubmit,
}: {
  company: CompanyRecord
  submitting: boolean
  onSubmit: (payload: EditableFields) => void
}) {
  const [form, setForm] = useState<EditableFields>({
    name: company.name,
    email: company.email,
    phoneNumber: company.phoneNumber,
    city: company.city,
    state: company.state,
    status: company.status,
    commissionRate: company.commissionRate ?? 10,
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(form)
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Company name</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          required
          type="text"
          value={form.name}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Email</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          required
          type="email"
          value={form.email}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Phone</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, phoneNumber: e.target.value }))}
          required
          type="text"
          value={form.phoneNumber}
        />
      </label>

      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">City</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
            required
            type="text"
            value={form.city}
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">State</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, state: e.target.value }))}
            required
            type="text"
            value={form.state}
          />
        </label>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Status</span>
          <select
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, status: e.target.value as CompanyRecord['status'] }))}
            value={form.status}
          >
            <option value="PENDING">Pending</option>
            <option value="ACTIVE">Active</option>
            <option value="SUSPENDED">Suspended</option>
            <option value="INACTIVE">Inactive</option>
          </select>
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Commission rate (%)</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, commissionRate: Number(e.target.value) }))}
            step="0.01"
            type="number"
            value={form.commissionRate}
          />
        </label>
      </div>

      <button
        className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-teal-300"
        disabled={submitting}
        type="submit"
      >
        {submitting ? <Loader2 className="animate-spin" size={18} /> : null}
        Save changes
      </button>
    </form>
  )
}

export default function AdminCompaniesPage() {
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState<CompanyRecord | null>(null)
  const [registering, setRegistering] = useState(false)

  const companiesQuery = useQuery({ queryKey: ['companies'], queryFn: listCompaniesRequest })
  const companies = companiesQuery.data ?? []

  const registerMutation = useMutation({
    mutationFn: async (form: RegisterFields) => {
      const company = await createCompanyRequest(buildPlaceholderCompanyPayload(form))
      return inviteCompanyAdminRequest({
        email: form.adminEmail,
        companyId: company.id,
        firstName: form.adminFirstName || undefined,
        lastName: form.adminLastName || undefined,
        phoneNumber: form.adminPhoneNumber || undefined,
      })
    },
    onSuccess: (data) => {
      toast.success(`Company registered and invite sent to ${data.invite.email}.`)
      if (data.setupUrl) {
        toast(`Dev setup link: ${data.setupUrl}`, { duration: 8000 })
      }
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      setRegistering(false)
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to register the company')),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: EditableFields }) => updateCompanyRequest(id, payload),
    onSuccess: () => {
      toast.success('Company updated.')
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      setEditing(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to update company')),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCompanyRequest,
    onSuccess: () => {
      toast.success('Company deleted.')
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to delete company')),
  })

  function handleDelete(company: CompanyRecord) {
    if (
      window.confirm(
        `Delete "${company.name}"? This will also delete all of its buses, routes, trips, and bookings. This cannot be undone.`,
      )
    ) {
      deleteMutation.mutate(company.id)
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">Companies</h1>
        <button
          className="flex items-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500"
          onClick={() => setRegistering(true)}
          type="button"
        >
          <Plus size={16} /> Register Company
        </button>
      </div>

      {companiesQuery.isLoading ? (
        <section className="card flex items-center gap-3 p-6 text-slate-600">
          <Loader2 className="animate-spin" size={18} />
          Loading companies...
        </section>
      ) : null}

      {companiesQuery.isError ? (
        <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700">
          <AlertCircle size={18} className="mt-0.5" />
          <p>{getApiErrorMessage(companiesQuery.error, 'Unable to load companies')}</p>
        </section>
      ) : null}

      {!companiesQuery.isLoading && !companiesQuery.isError ? (
        companies.length ? (
          <section className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <th className="px-5 py-3">ID</th>
                    <th className="px-5 py-3">Name</th>
                    <th className="px-5 py-3">Email</th>
                    <th className="px-5 py-3">Phone</th>
                    <th className="px-5 py-3">Location</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3">Registration</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {companies.map((company, index) => (
                    <tr key={company.id} className="hover:bg-slate-50">
                      <td className="px-5 py-3 font-medium text-slate-500">{index + 1}</td>
                      <td className="px-5 py-3 font-medium text-slate-800">{company.name}</td>
                      <td className="px-5 py-3 text-slate-600">{company.email}</td>
                      <td className="px-5 py-3 text-slate-600">{company.phoneNumber}</td>
                      <td className="px-5 py-3 text-slate-600">{company.city}, {company.state}</td>
                      <td className="px-5 py-3">
                        <span
                          className={`rounded-full px-2 py-1 text-xs font-semibold ${
                            company.status === 'ACTIVE'
                              ? 'bg-emerald-100 text-emerald-700'
                              : company.status === 'PENDING'
                                ? 'bg-amber-100 text-amber-700'
                                : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {company.status}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-slate-500">{company.registrationNumber}</td>
                      <td className="px-5 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-teal-700"
                            onClick={() => setEditing(company)}
                            type="button"
                          >
                            <Pencil size={16} />
                          </button>
                          <button
                            className="rounded-lg p-2 text-slate-500 hover:bg-rose-50 hover:text-rose-600"
                            onClick={() => handleDelete(company)}
                            type="button"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : (
          <section className="card flex flex-col items-center gap-3 p-12 text-center text-slate-400">
            <Building2 size={32} />
            <p>No companies registered yet</p>
          </section>
        )
      ) : null}

      {editing ? (
        <Modal onClose={() => setEditing(null)} title={`Edit ${editing.name}`}>
          <EditCompanyForm
            company={editing}
            onSubmit={(payload) => updateMutation.mutate({ id: editing.id, payload })}
            submitting={updateMutation.isPending}
          />
        </Modal>
      ) : null}

      {registering ? (
        <Modal onClose={() => setRegistering(false)} title="Register a bus company">
          <RegisterCompanyForm
            onSubmit={(payload) => registerMutation.mutate(payload)}
            submitting={registerMutation.isPending}
          />
        </Modal>
      ) : null}
    </section>
  )
}
