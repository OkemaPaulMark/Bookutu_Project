import { FormEvent, useState } from 'react'
import { ArrowRight, BusFront, Loader2, ShieldCheck } from 'lucide-react'
import { Navigate, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '@store/authStore'
import { getApiErrorMessage } from '@/lib/api'

export default function LoginPage() {
  const user = useAuthStore((state) => state.user)
  const login = useAuthStore((state) => state.login)
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to={user.role === 'SUPER_ADMIN' ? '/admin' : '/company'} replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)

    try {
      const loggedInUser = await login({ email, password })
      toast.success(`Welcome back, ${loggedInUser.firstName ?? loggedInUser.name}.`)
      navigate(loggedInUser.role === 'SUPER_ADMIN' ? '/admin' : '/company')
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Unable to sign in right now'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
        <div className="relative hidden overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(45,212,191,0.28),_transparent_38%),linear-gradient(135deg,_#020617_0%,_#0f172a_48%,_#134e4a_100%)] p-12 lg:flex lg:flex-col lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-white/10 p-3 ring-1 ring-white/15">
              <BusFront size={22} />
            </div>
            <div>
              <p className="text-lg font-semibold">Bookutu</p>
              <p className="text-sm text-slate-300">Transport operations control</p>
            </div>
          </div>

          <div className="max-w-xl">
            <p className="text-sm uppercase tracking-[0.2em] text-teal-200/80">Dashboard Access</p>
            <h1 className="mt-6 text-5xl font-semibold leading-tight">
              Sign in to manage routes, companies, and platform operations.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-slate-300">
              Super admins work from Bookutu HQ. Company admins use the invite email from Bookutu to set their password before they log in here.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <article className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <ShieldCheck className="text-teal-300" size={18} />
              <h2 className="mt-4 text-lg font-semibold">Bookutu HQ</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                Register bus company admins, review platform activity, and manage the wider system.
              </p>
            </article>
            <article className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <ArrowRight className="text-cyan-300" size={18} />
              <h2 className="mt-4 text-lg font-semibold">Company access</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                Use the password setup link from your invite email once, then log in normally from this page.
              </p>
            </article>
          </div>
        </div>

        <div className="flex items-center justify-center bg-slate-100 px-6 py-10">
          <section className="w-full max-w-md rounded-[28px] border border-slate-200 bg-white p-8 shadow-2xl shadow-slate-300/30">
            <div className="flex items-center gap-3 lg:hidden">
              <div className="rounded-2xl bg-teal-600 p-3 text-white">
                <BusFront size={20} />
              </div>
              <div>
                <p className="text-lg font-semibold text-slate-900">Bookutu</p>
                <p className="text-sm text-slate-500">Dashboard access</p>
              </div>
            </div>

            <div className="mt-8">
              <p className="text-sm font-medium uppercase tracking-[0.18em] text-teal-700">Welcome back</p>
              <h2 className="mt-3 text-3xl font-semibold text-slate-900">Login to continue</h2>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Use your Bookutu admin or company admin email and password.
              </p>
            </div>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">Email address</span>
                <input
                  autoComplete="email"
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="admin@bookutu.com"
                  required
                  type="email"
                  value={email}
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">Password</span>
                <input
                  autoComplete="current-password"
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  required
                  type="password"
                  value={password}
                />
              </label>

              <button
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-teal-300"
                disabled={submitting}
                type="submit"
              >
                {submitting ? <Loader2 className="animate-spin" size={18} /> : null}
                Sign in
              </button>
            </form>
          </section>
        </div>
      </section>
    </main>
  )
}
