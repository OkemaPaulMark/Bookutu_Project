import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, Loader2, Megaphone, Pencil, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import Modal from '@components/Modal'
import { getApiErrorMessage } from '@/lib/api'
import {
  AdvertPayload,
  AdvertRecord,
  createAdvertRequest,
  deleteAdvertRequest,
  listAdvertsRequest,
  updateAdvertRequest,
} from '@/lib/adverts'

const emptyForm: AdvertPayload = { title: '', description: '', imageUrl: '', linkUrl: '', isActive: true }

function AdvertForm({
  initial,
  submitting,
  submitLabel,
  onSubmit,
}: {
  initial: AdvertPayload
  submitting: boolean
  submitLabel: string
  onSubmit: (payload: AdvertPayload) => void
}) {
  const [form, setForm] = useState(initial)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(form)
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Title</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          required
          type="text"
          value={form.title}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Description</span>
        <textarea
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          rows={3}
          value={form.description}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Image URL</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, imageUrl: e.target.value }))}
          placeholder="https://..."
          required
          type="url"
          value={form.imageUrl}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-medium text-slate-700">Link URL (optional)</span>
        <input
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
          onChange={(e) => setForm((f) => ({ ...f, linkUrl: e.target.value }))}
          placeholder="https://..."
          type="url"
          value={form.linkUrl ?? ''}
        />
      </label>

      <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
        <input
          checked={form.isActive ?? true}
          onChange={(e) => setForm((f) => ({ ...f, isActive: e.target.checked }))}
          type="checkbox"
        />
        Active
      </label>

      <button
        className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-teal-300"
        disabled={submitting}
        type="submit"
      >
        {submitting ? <Loader2 className="animate-spin" size={18} /> : null}
        {submitLabel}
      </button>
    </form>
  )
}

export default function AdminAdvertsPage() {
  const queryClient = useQueryClient()
  const [modal, setModal] = useState<'create' | AdvertRecord | null>(null)

  const advertsQuery = useQuery({ queryKey: ['adverts'], queryFn: listAdvertsRequest })
  const adverts = advertsQuery.data ?? []

  const createMutation = useMutation({
    mutationFn: createAdvertRequest,
    onSuccess: () => {
      toast.success('Advert created.')
      queryClient.invalidateQueries({ queryKey: ['adverts'] })
      setModal(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to create advert')),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<AdvertPayload> }) => updateAdvertRequest(id, payload),
    onSuccess: () => {
      toast.success('Advert updated.')
      queryClient.invalidateQueries({ queryKey: ['adverts'] })
      setModal(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to update advert')),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteAdvertRequest,
    onSuccess: () => {
      toast.success('Advert deleted.')
      queryClient.invalidateQueries({ queryKey: ['adverts'] })
    },
    onError: (error) => toast.error(getApiErrorMessage(error, 'Unable to delete advert')),
  })

  function handleDelete(advert: AdvertRecord) {
    if (window.confirm(`Delete "${advert.title}"? This cannot be undone.`)) {
      deleteMutation.mutate(advert.id)
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">Adverts</h1>
        <button
          className="flex items-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500"
          onClick={() => setModal('create')}
          type="button"
        >
          <Plus size={16} /> New advert
        </button>
      </div>

      {advertsQuery.isLoading ? (
        <section className="card flex items-center gap-3 p-6 text-slate-600">
          <Loader2 className="animate-spin" size={18} />
          Loading adverts...
        </section>
      ) : null}

      {advertsQuery.isError ? (
        <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700">
          <AlertCircle size={18} className="mt-0.5" />
          <p>{getApiErrorMessage(advertsQuery.error, 'Unable to load adverts')}</p>
        </section>
      ) : null}

      {!advertsQuery.isLoading && !advertsQuery.isError ? (
        adverts.length ? (
          <section className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <th className="px-5 py-3">ID</th>
                    <th className="px-5 py-3">Advert</th>
                    <th className="px-5 py-3">Link</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3">Created</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {adverts.map((advert, index) => (
                    <tr key={advert.id} className="hover:bg-slate-50">
                      <td className="px-5 py-3 font-medium text-slate-500">{index + 1}</td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-3">
                          <img
                            alt=""
                            className="h-12 w-12 rounded-xl object-cover"
                            src={advert.imageUrl}
                          />
                          <div>
                            <p className="font-medium text-slate-800">{advert.title}</p>
                            <p className="max-w-xs truncate text-xs text-slate-500">{advert.description}</p>
                          </div>
                        </div>
                      </td>
                      <td className="max-w-[160px] truncate px-5 py-3 text-slate-500">
                        {advert.linkUrl || '—'}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className={`rounded-full px-2 py-1 text-xs font-semibold ${
                            advert.isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {advert.isActive ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-slate-500">
                        {new Date(advert.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-teal-700"
                            onClick={() => setModal(advert)}
                            type="button"
                          >
                            <Pencil size={16} />
                          </button>
                          <button
                            className="rounded-lg p-2 text-slate-500 hover:bg-rose-50 hover:text-rose-600"
                            onClick={() => handleDelete(advert)}
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
            <Megaphone size={32} />
            <p>No adverts created yet</p>
          </section>
        )
      ) : null}

      {modal === 'create' ? (
        <Modal onClose={() => setModal(null)} title="New advert">
          <AdvertForm
            initial={emptyForm}
            onSubmit={(payload) => createMutation.mutate(payload)}
            submitLabel="Create advert"
            submitting={createMutation.isPending}
          />
        </Modal>
      ) : null}

      {modal && modal !== 'create' ? (
        <Modal onClose={() => setModal(null)} title="Edit advert">
          <AdvertForm
            initial={{
              title: modal.title,
              description: modal.description,
              imageUrl: modal.imageUrl,
              linkUrl: modal.linkUrl ?? '',
              isActive: modal.isActive,
            }}
            onSubmit={(payload) => updateMutation.mutate({ id: modal.id, payload })}
            submitLabel="Save changes"
            submitting={updateMutation.isPending}
          />
        </Modal>
      ) : null}
    </section>
  )
}
