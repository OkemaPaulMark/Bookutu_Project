import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, AlertCircle, Pencil, Trash2, Copy } from 'lucide-react'
import toast from 'react-hot-toast'
import { listUsersRequest, updateUserRequest, deleteUserRequest } from '@/lib/users'
import { inviteCompanyAdminRequest } from '@/lib/companies'
import type { AuthApiUser } from '@/lib/auth'
import { getApiErrorMessage } from '@/lib/api'
import { useAuthStore } from '@store/authStore'

const emptyInviteForm = { email: '', firstName: '', lastName: '', phoneNumber: '' }

type EditForm = { firstName: string; lastName: string; phoneNumber: string }

export default function CompanyStaffPage() {
  const currentUser = useAuthStore(s => s.user)
  const qc = useQueryClient()
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteForm, setInviteForm] = useState(emptyInviteForm)
  const [editingStaff, setEditingStaff] = useState<AuthApiUser | null>(null)
  const [editForm, setEditForm] = useState<EditForm>({ firstName: '', lastName: '', phoneNumber: '' })
  const [justInvited, setJustInvited] = useState<{ email: string; setupUrl: string } | null>(null)

  const staffQuery = useQuery({ queryKey: ['staff'], queryFn: () => listUsersRequest({ userType: 'COMPANY_STAFF' }) })

  const inviteMutation = useMutation({
    mutationFn: inviteCompanyAdminRequest,
    onSuccess: (result) => {
      qc.invalidateQueries({ queryKey: ['staff'] })
      toast.success(`Invite sent to ${result.invite.email}`)
      if (result.setupUrl) setJustInvited({ email: result.invite.email, setupUrl: result.setupUrl })
      setShowInviteModal(false)
      setInviteForm(emptyInviteForm)
    },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to invite staff member'))
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<EditForm> }) => updateUserRequest(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['staff'] }); toast.success('Staff member updated'); setEditingStaff(null) },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to update staff member'))
  })

  const deleteMutation = useMutation({
    mutationFn: deleteUserRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['staff'] }); toast.success('Staff member removed') },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to remove staff member'))
  })

  function handleInviteChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target
    setInviteForm(prev => ({ ...prev, [name]: value }))
  }

  function handleInviteSubmit(e: FormEvent) {
    e.preventDefault()
    if (!currentUser?.companyId) return
    inviteMutation.mutate({ ...inviteForm, companyId: currentUser.companyId })
  }

  function openEdit(staff: AuthApiUser) {
    setEditingStaff(staff)
    setEditForm({
      firstName: staff.firstName ?? '',
      lastName: staff.lastName ?? '',
      phoneNumber: staff.phoneNumber ?? ''
    })
  }

  function handleEditChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target
    setEditForm(prev => ({ ...prev, [name]: value }))
  }

  function handleEditSubmit(e: FormEvent) {
    e.preventDefault()
    if (!editingStaff) return
    updateMutation.mutate({ id: editingStaff.id, payload: editForm })
  }

  function handleDelete(staff: AuthApiUser) {
    if (window.confirm(`Remove ${staff.email} from staff? This cannot be undone.`)) {
      deleteMutation.mutate(staff.id)
    }
  }

  function copyLink(url: string) {
    navigator.clipboard.writeText(url)
    toast.success('Setup link copied')
  }

  const staff = staffQuery.data ?? []

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Staff</h1>
          <p className="mt-1 text-sm text-slate-600">Manage who can log in and help run this dashboard</p>
        </div>
        <button onClick={() => setShowInviteModal(true)} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition">
          <Plus size={18} /> Invite Staff
        </button>
      </div>

      {justInvited && (
        <div className="card flex items-center justify-between border-emerald-200 bg-emerald-50 p-4">
          <div>
            <p className="text-sm text-emerald-800">Invite sent to <span className="font-semibold">{justInvited.email}</span>. Dev setup link:</p>
            <p className="mt-1 break-all font-mono text-xs text-emerald-900">{justInvited.setupUrl}</p>
          </div>
          <div className="flex items-center gap-2 pl-4">
            <button onClick={() => copyLink(justInvited.setupUrl)} className="flex items-center gap-1 rounded-lg border border-emerald-300 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-100 transition">
              <Copy size={14} /> Copy
            </button>
            <button onClick={() => setJustInvited(null)}><X size={18} className="text-emerald-700" /></button>
          </div>
        </div>
      )}

      {staffQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading staff...</div>}
      {staffQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(staffQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Name', 'Email', 'Phone', 'Verified', 'Joined', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {staff.length === 0 && !staffQuery.isLoading ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-500">No staff registered yet</td></tr>
              ) : staff.map((member: AuthApiUser) => (
                <tr key={member.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 text-sm font-medium text-slate-900">
                    {[member.firstName, member.lastName].filter(Boolean).join(' ') || '—'}
                    {member.id === currentUser?.id && <span className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">You</span>}
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-600">{member.email}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">{member.phoneNumber || '—'}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${member.isVerified ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                      {member.isVerified ? 'Active' : 'Invite pending'}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-600">{member.createdAt ? new Date(member.createdAt).toLocaleDateString() : '—'}</td>
                  <td className="px-6 py-3 text-sm">
                    <div className="flex items-center gap-1">
                      <button onClick={() => openEdit(member)} title="Edit" className="rounded p-1.5 text-amber-700 hover:bg-amber-50 transition">
                        <Pencil size={15} />
                      </button>
                      {member.id !== currentUser?.id && (
                        <button onClick={() => handleDelete(member)} disabled={deleteMutation.isPending} title="Remove" className="rounded p-1.5 text-rose-700 hover:bg-rose-50 transition disabled:opacity-50">
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card max-h-[90vh] w-full max-w-md overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900">Invite Staff</h2>
              <button onClick={() => setShowInviteModal(false)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleInviteSubmit} className="space-y-4 p-6">
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Email</span><input name="email" type="email" value={inviteForm.email} onChange={handleInviteChange} required className="input" placeholder="staff@example.com" /></label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">First Name</span><input name="firstName" value={inviteForm.firstName} onChange={handleInviteChange} className="input" placeholder="Moses" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Last Name</span><input name="lastName" value={inviteForm.lastName} onChange={handleInviteChange} className="input" placeholder="Okello" /></label>
              </div>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Phone Number</span><input name="phoneNumber" value={inviteForm.phoneNumber} onChange={handleInviteChange} className="input" placeholder="+256701000000" /></label>
              <p className="text-xs text-slate-500">They'll receive an email with a link to set their password and log in.</p>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowInviteModal(false)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={inviteMutation.isPending} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {inviteMutation.isPending && <Loader2 size={15} className="animate-spin" />}
                  Send Invite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editingStaff && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card max-h-[90vh] w-full max-w-md overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900">Edit Staff</h2>
              <button onClick={() => setEditingStaff(null)}><X size={20} className="text-slate-500" /></button>
            </div>
            <form onSubmit={handleEditSubmit} className="space-y-4 p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">First Name</span><input name="firstName" value={editForm.firstName} onChange={handleEditChange} className="input" /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Last Name</span><input name="lastName" value={editForm.lastName} onChange={handleEditChange} className="input" /></label>
              </div>
              <label className="block"><span className="mb-1 block text-sm font-medium text-slate-700">Phone Number</span><input name="phoneNumber" value={editForm.phoneNumber} onChange={handleEditChange} className="input" /></label>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setEditingStaff(null)} className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={updateMutation.isPending} className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {updateMutation.isPending && <Loader2 size={15} className="animate-spin" />}
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}
