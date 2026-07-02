import { FormEvent, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { KeyRound, Loader2, Save, UserCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { changePasswordRequest, updateProfileRequest } from '@/lib/auth'
import { useAuthStore } from '@store/authStore'

type Tab = 'profile' | 'password'

const tabs: { id: Tab; label: string; icon: typeof UserCircle2 }[] = [
  { id: 'profile', label: 'Personal Profile', icon: UserCircle2 },
  { id: 'password', label: 'Change Password', icon: KeyRound },
]

function Field({ label, value, onChange, type = 'text', disabled }: {
  label: string; value: string; onChange: (v: string) => void
  type?: string; disabled?: boolean
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-slate-700">{label}</span>
      <input
        className="input"
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
      />
    </label>
  )
}

export default function AdminSettingsPage() {
  const user = useAuthStore(s => s.user)
  const [tab, setTab] = useState<Tab>('profile')

  const [firstName, setFirstName] = useState(user?.firstName ?? '')
  const [lastName, setLastName] = useState(user?.lastName ?? '')
  const [phone, setPhone] = useState(user?.phoneNumber ?? '')

  const profileMutation = useMutation({
    mutationFn: () => updateProfileRequest({ firstName, lastName, phoneNumber: phone }),
    onSuccess: () => toast.success('Profile updated'),
    onError: () => toast.error('Failed to update profile'),
  })

  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')

  const passwordMutation = useMutation({
    mutationFn: () => changePasswordRequest({ currentPassword: currentPw, newPassword: newPw }),
    onSuccess: () => {
      toast.success('Password changed')
      setCurrentPw(''); setNewPw(''); setConfirmPw('')
    },
    onError: () => toast.error('Failed to change password'),
  })

  function handlePasswordSubmit(e: FormEvent) {
    e.preventDefault()
    if (newPw !== confirmPw) { toast.error('Passwords do not match'); return }
    if (newPw.length < 8) { toast.error('Password must be at least 8 characters'); return }
    passwordMutation.mutate()
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">Manage your account preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar tabs */}
        <nav className="w-52 shrink-0 space-y-1">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                tab === t.id
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
              type="button"
            >
              <t.icon size={16} />
              {t.label}
            </button>
          ))}
        </nav>

        {/* Panel */}
        <div className="flex-1">
          {tab === 'profile' && (
            <div className="card p-6">
              <div className="mb-6 flex items-center gap-3 border-b border-slate-100 pb-5">
                <div className="rounded-lg bg-blue-50 p-2 text-blue-600"><UserCircle2 size={18} /></div>
                <div>
                  <h2 className="font-semibold text-slate-900">Personal Profile</h2>
                  <p className="text-sm text-slate-500">Update your name and contact details</p>
                </div>
              </div>

              <form
                className="space-y-5"
                onSubmit={e => { e.preventDefault(); profileMutation.mutate() }}
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label="First name" value={firstName} onChange={setFirstName} />
                  <Field label="Last name" value={lastName} onChange={setLastName} />
                  <div className="sm:col-span-2">
                    <Field label="Phone number" value={phone} onChange={setPhone} />
                  </div>
                  <div className="sm:col-span-2">
                    <Field label="Email address" value={user?.email ?? ''} onChange={() => {}} disabled />
                  </div>
                  <div className="sm:col-span-2">
                    <Field label="Role" value="Super Admin" onChange={() => {}} disabled />
                  </div>
                </div>

                <div className="flex justify-end border-t border-slate-100 pt-5">
                  <button
                    className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                    disabled={profileMutation.isPending}
                    type="submit"
                  >
                    {profileMutation.isPending ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}
                    Save changes
                  </button>
                </div>
              </form>
            </div>
          )}

          {tab === 'password' && (
            <div className="card p-6">
              <div className="mb-6 flex items-center gap-3 border-b border-slate-100 pb-5">
                <div className="rounded-lg bg-amber-50 p-2 text-amber-600"><KeyRound size={18} /></div>
                <div>
                  <h2 className="font-semibold text-slate-900">Change Password</h2>
                  <p className="text-sm text-slate-500">Use a strong password of at least 8 characters</p>
                </div>
              </div>

              <form className="space-y-5 max-w-md" onSubmit={handlePasswordSubmit}>
                <Field label="Current password" value={currentPw} onChange={setCurrentPw} type="password" />
                <Field label="New password" value={newPw} onChange={setNewPw} type="password" />
                <Field label="Confirm new password" value={confirmPw} onChange={setConfirmPw} type="password" />

                <div className="flex justify-end border-t border-slate-100 pt-5">
                  <button
                    className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                    disabled={passwordMutation.isPending}
                    type="submit"
                  >
                    {passwordMutation.isPending ? <Loader2 size={15} className="animate-spin" /> : <KeyRound size={15} />}
                    Update password
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
