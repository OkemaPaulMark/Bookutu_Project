import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, Loader2, Pencil, Trash2, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import Modal from '@components/Modal'
import type { AuthApiUser } from '@/lib/auth'
import { deleteUserRequest, listUsersRequest, updateUserRequest } from '@/lib/users'
import { getApiErrorMessage } from '@/lib/api'

type EditableFields = {
  firstName: string
  lastName: string
  phoneNumber: string
  email: string
  isActive: boolean
  isVerified: boolean
}

function EditPassengerForm({
  passenger,
  submitting,
  onSubmit,
}: {
  passenger: AuthApiUser
  submitting: boolean
  onSubmit: (payload: EditableFields) => void
}) {
  const [form, setForm] = useState<EditableFields>({
    firstName: passenger.firstName ?? '',
    lastName: passenger.lastName ?? '',
    phoneNumber: passenger.phoneNumber ?? '',
    email: passenger.email,
    isActive: true,
    isVerified: passenger.isVerified,
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(form)
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">First name</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, firstName: e.target.value }))}
            type="text"
            value={form.firstName}
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Last name</span>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
            onChange={(e) => setForm((f) => ({ ...f, lastName: e.target.value }))}
            type="text"
            value={form.lastName}
          />
        </label>
      </div>

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
          type="text"
          value={form.phoneNumber}
        />
      </label>

      <div className="flex gap-6">
        <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
          <input
            checked={form.isActive}
            onChange={(e) => setForm((f) => ({ ...f, isActive: e.target.checked }))}
            type="checkbox"
          />
          Active
        </label>
        <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
          <input
            checked={form.isVerified}
            onChange={(e) => setForm((f) => ({ ...f, isVerified: e.target.checked }))}
            type="checkbox"
          />
          Verified
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

export default function CompanyPassengersPage() {
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState<AuthApiUser | null>(null)

  const passengersQuery = useQuery({
    queryKey: ['passengers'],
    queryFn: () => listUsersRequest({ userType: 'PASSENGER' })
  })
  const passengers = passengersQuery.data ?? []

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: EditableFields }) => updateUserRequest(id, payload),
    onSuccess: () => {
      toast.success('Passenger updated.')
      queryClient.invalidateQueries({ queryKey: ['passengers'] })
      setEditing(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to update passenger')),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteUserRequest,
    onSuccess: () => {
      toast.success('Passenger deleted.')
      queryClient.invalidateQueries({ queryKey: ['passengers'] })
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to delete passenger')),
  })

  function handleDelete(passenger: AuthApiUser) {
    if (window.confirm(`Delete ${passenger.email}? This will also delete their bookings. This cannot be undone.`)) {
      deleteMutation.mutate(passenger.id)
    }
  }

  return (
    <section className="space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Passengers</h1>

      {passengersQuery.isLoading ? (
        <section className="card flex items-center gap-3 p-6 text-slate-600">
          <Loader2 className="animate-spin" size={18} />
          Loading passengers...
        </section>
      ) : null}

      {passengersQuery.isError ? (
        <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700">
          <AlertCircle size={18} className="mt-0.5" />
          <p>{getApiErrorMessage(passengersQuery.error, 'Unable to load passengers')}</p>
        </section>
      ) : null}

      {!passengersQuery.isLoading && !passengersQuery.isError ? (
        passengers.length ? (
          <section className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <th className="px-5 py-3">ID</th>
                    <th className="px-5 py-3">Name</th>
                    <th className="px-5 py-3">Email</th>
                    <th className="px-5 py-3">Phone</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3">Registered</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {passengers.map((passenger, index) => {
                    const name = [passenger.firstName, passenger.lastName].filter(Boolean).join(' ') || '—'
                    return (
                      <tr key={passenger.id} className="hover:bg-slate-50">
                        <td className="px-5 py-3 font-medium text-slate-500">{index + 1}</td>
                        <td className="px-5 py-3 font-medium text-slate-800">{name}</td>
                        <td className="px-5 py-3 text-slate-600">{passenger.email}</td>
                        <td className="px-5 py-3 text-slate-600">{passenger.phoneNumber || '—'}</td>
                        <td className="px-5 py-3">
                          <span
                            className={`rounded-full px-2 py-1 text-xs font-semibold ${
                              passenger.isVerified
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-amber-100 text-amber-700'
                            }`}
                          >
                            {passenger.isVerified ? 'Verified' : 'Unverified'}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-slate-500">
                          {passenger.createdAt ? new Date(passenger.createdAt).toLocaleDateString() : '—'}
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-teal-700"
                              onClick={() => setEditing(passenger)}
                              type="button"
                            >
                              <Pencil size={16} />
                            </button>
                            <button
                              className="rounded-lg p-2 text-slate-500 hover:bg-rose-50 hover:text-rose-600"
                              onClick={() => handleDelete(passenger)}
                              type="button"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>
        ) : (
          <section className="card flex flex-col items-center gap-3 p-12 text-center text-slate-400">
            <Users size={32} />
            <p>No passengers registered yet</p>
          </section>
        )
      ) : null}

      {editing ? (
        <Modal onClose={() => setEditing(null)} title={`Edit ${editing.email}`}>
          <EditPassengerForm
            passenger={editing}
            onSubmit={(payload) => updateMutation.mutate({ id: editing.id, payload })}
            submitting={updateMutation.isPending}
          />
        </Modal>
      ) : null}
    </section>
  )
}
