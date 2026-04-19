import { ShieldCheck, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'

export default function LoginPage() {
  const loginAs = useAuthStore((state) => state.loginAs)
  const navigate = useNavigate()

  function handleSelect(role: 'SUPER_ADMIN' | 'COMPANY_STAFF') {
    loginAs(role)
    navigate(role === 'SUPER_ADMIN' ? '/admin' : '/company')
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <section className="card w-full max-w-3xl p-8">
        <h1 className="text-3xl font-bold text-slate-800">Bookutu Dashboard Access</h1>
        <p className="mt-2 text-slate-600">Single app, role-based experience.</p>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <button
            type="button"
            onClick={() => handleSelect('SUPER_ADMIN')}
            className="card border-blue-200 p-6 text-left hover:bg-blue-50"
          >
            <ShieldCheck className="text-blue-600" />
            <h2 className="mt-3 text-lg font-semibold">Login as Super Admin</h2>
            <p className="mt-1 text-sm text-slate-600">Platform control, companies, financial oversight.</p>
          </button>

          <button
            type="button"
            onClick={() => handleSelect('COMPANY_STAFF')}
            className="card border-emerald-200 p-6 text-left hover:bg-emerald-50"
          >
            <Users className="text-emerald-600" />
            <h2 className="mt-3 text-lg font-semibold">Login as Company Staff</h2>
            <p className="mt-1 text-sm text-slate-600">Fleet, routes, trips, direct bookings and reports.</p>
          </button>
        </div>
      </section>
    </main>
  )
}
