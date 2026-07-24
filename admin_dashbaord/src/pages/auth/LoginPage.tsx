import { FormEvent, useState } from 'react'
import { BusFront, Eye, EyeOff, Loader2, ShieldCheck, Users } from 'lucide-react'
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
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/company" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)

    try {
      const loggedInUser = await login({ email, password })
      toast.success(`Welcome back, ${loggedInUser.firstName ?? loggedInUser.name}.`)
      navigate('/company')
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Unable to sign in right now'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
        <div className="relative hidden overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.25),_transparent_38%),linear-gradient(135deg,_#020617_0%,_#0f172a_48%,_#1e3a8a_100%)] p-12 lg:flex lg:flex-col lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-white/10 p-3 ring-1 ring-white/15">
              <BusFront size={22} />
            </div>
            <p className="text-lg font-semibold">Bookutu</p>
          </div>

          <div className="max-w-xl">
            <h1 className="text-5xl font-semibold leading-tight">
              Run your bus company from one dashboard.
            </h1>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <article className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <ShieldCheck className="text-blue-300" size={18} />
              <h2 className="mt-4 text-base font-semibold">Fleet to finances</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                Fleet, routes, trips, bookings, deliveries, and more — all in one place.
              </p>
            </article>
            <article className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <Users className="text-cyan-300" size={18} />
              <h2 className="mt-4 text-base font-semibold">One team, one view</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                Invite staff and give everyone the same live data.
              </p>
            </article>
          </div>
        </div>

        <div className="flex items-center justify-center bg-slate-100 px-6 py-10">
          <section className="w-full max-w-md rounded-[28px] border border-slate-200 bg-white p-8 shadow-2xl shadow-slate-300/30">
            <div className="flex items-center gap-3 lg:hidden">
              <div className="rounded-2xl bg-blue-600 p-3 text-white">
                <BusFront size={20} />
              </div>
              <p className="text-lg font-semibold text-slate-900">Bookutu</p>
            </div>

            <div className="mt-8 lg:mt-0">
              <p className="text-sm font-medium uppercase tracking-[0.18em] text-blue-700">Welcome back</p>
              <h2 className="mt-3 text-3xl font-semibold text-slate-900">Login to continue</h2>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Use your staff email and password.
              </p>
            </div>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">Email address</span>
                <input
                  autoComplete="email"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white"
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@company.com"
                  required
                  type="email"
                  value={email}
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">Password</span>
                <div className="relative">
                  <input
                    autoComplete="current-password"
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 pr-11 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white"
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    required
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                  />
                  <button
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    onClick={() => setShowPassword((s) => !s)}
                    type="button"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </label>

              <button
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
                disabled={submitting}
                type="submit"
              >
                {submitting ? <Loader2 className="animate-spin" size={18} /> : null}
                Sign in
              </button>
            </form>

            <p className="mt-6 text-center text-xs text-slate-400">
              New staff use the link from their invite email to set a password.
            </p>
          </section>
        </div>
      </section>
    </main>
  )
}
