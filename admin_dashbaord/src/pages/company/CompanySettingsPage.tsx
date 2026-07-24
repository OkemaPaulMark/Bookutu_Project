import { FormEvent, useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Building2, KeyRound, Loader2, Save, UserCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { getCompanyRequest, updateCompanyRequest } from '@/lib/companies'
import { changePasswordRequest, updateProfileRequest } from '@/lib/auth'
import { useAuthStore } from '@store/authStore'

type Tab = 'company' | 'profile' | 'password'

const tabs: { id: Tab; label: string; icon: typeof Building2 }[] = [
  { id: 'company', label: 'Company Profile', icon: Building2 },
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

export default function CompanySettingsPage() {
  const user = useAuthStore(s => s.user)
  const queryClient = useQueryClient()
  const companyId = user?.companyId ?? ''
  const [tab, setTab] = useState<Tab>('company')

  // Company form state
  const companyQuery = useQuery({
    queryKey: ['company', companyId],
    queryFn: () => getCompanyRequest(companyId),
    enabled: Boolean(companyId),
  })
  const [cName, setCName] = useState('')
  const [cEmail, setCEmail] = useState('')
  const [cPhone, setCPhone] = useState('')
  const [cAddress, setCAddress] = useState('')
  const [cCity, setCCity] = useState('')
  const [cState, setCState] = useState('')
  const [cLicense, setCLicense] = useState('')
  const [cWebsite, setCWebsite] = useState('')

  useEffect(() => {
    const d = companyQuery.data
    if (!d) return
    setCName(d.name ?? '')
    setCEmail(d.email ?? '')
    setCPhone(d.phoneNumber ?? '')
    setCAddress(d.address ?? '')
    setCCity(d.city ?? '')
    setCState(d.state ?? '')
    setCLicense(d.licenseNumber ?? '')
    setCWebsite(d.website ?? '')
  }, [companyQuery.data])

  const companyMutation = useMutation({
    mutationFn: () => updateCompanyRequest(companyId, {
      name: cName, email: cEmail, phoneNumber: cPhone,
      address: cAddress, city: cCity, state: cState,
      licenseNumber: cLicense, website: cWebsite,
    }),
    onSuccess: async () => {
      toast.success('Company details saved')
      await queryClient.invalidateQueries({ queryKey: ['company', companyId] })
    },
    onError: () => toast.error('Failed to save company details'),
  })

  // Personal profile state
  const [firstName, setFirstName] = useState(user?.firstName ?? '')
  const [lastName, setLastName] = useState(user?.lastName ?? '')
  const [phone, setPhone] = useState(user?.phoneNumber ?? '')

  const profileMutation = useMutation({
    mutationFn: () => updateProfileRequest({ firstName, lastName, phoneNumber: phone }),
    onSuccess: () => toast.success('Profile updated'),
    onError: () => toast.error('Failed to update profile'),
  })

  // Password state
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
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900">Settings</h1>
        <p className="mt-1 text-sm text-slate-600">Manage your company profile and account preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar tabs */}
        <nav className="card h-fit w-56 shrink-0 space-y-1 p-2">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                tab === t.id
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
              type="button"
            >
              {tab === t.id && <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-blue-600" />}
              <t.icon size={16} />
              {t.label}
            </button>
          ))}
        </nav>

        {/* Panel */}
        <div className="flex-1">
          {/* Company Profile */}
          {tab === 'company' && (
            <div className="card p-6">
              <div className="mb-6 flex items-center gap-3 border-b border-slate-100 pb-5">
                <div className="rounded-lg bg-blue-50 p-2 text-blue-600"><Building2 size={18} /></div>
                <div>
                  <h2 className="font-semibold text-slate-900">Company Profile</h2>
                  <p className="text-sm text-slate-500">Update your company's public information</p>
                </div>
              </div>

              {companyQuery.isLoading
                ? <div className="flex items-center gap-2 text-sm text-slate-500"><Loader2 size={16} className="animate-spin" /> Loading...</div>
                : (
                  <form
                    className="space-y-5"
                    onSubmit={e => { e.preventDefault(); companyMutation.mutate() }}
                  >
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="sm:col-span-2">
                        <Field label="Company name" value={cName} onChange={setCName} />
                      </div>
                      <div className="sm:col-span-2">
                        <Field label="Email address" value={cEmail} onChange={setCEmail} type="email" />
                      </div>
                      <Field label="Phone number" value={cPhone} onChange={setCPhone} />
                      <Field label="Website" value={cWebsite} onChange={setCWebsite} />
                      <div className="sm:col-span-2">
                        <Field label="Address" value={cAddress} onChange={setCAddress} />
                      </div>
                      <Field label="City" value={cCity} onChange={setCCity} />
                      <Field label="State / Region" value={cState} onChange={setCState} />
                      <Field label="License number" value={cLicense} onChange={setCLicense} />
                      <Field label="Registration number" value={companyQuery.data?.registrationNumber ?? ''} onChange={() => {}} disabled />
                    </div>

                    <div className="flex justify-end border-t border-slate-100 pt-5">
                      <button
                        className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                        disabled={companyMutation.isPending}
                        type="submit"
                      >
                        {companyMutation.isPending ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}
                        Save changes
                      </button>
                    </div>
                  </form>
                )
              }
            </div>
          )}

          {/* Personal Profile */}
          {tab === 'profile' && (
            <div className="card p-6">
              <div className="mb-6 flex items-center gap-3 border-b border-slate-100 pb-5">
                <div className="rounded-lg bg-teal-50 p-2 text-teal-600"><UserCircle2 size={18} /></div>
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

          {/* Change Password */}
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
