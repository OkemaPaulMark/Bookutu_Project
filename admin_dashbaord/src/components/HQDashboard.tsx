import { useQuery } from '@tanstack/react-query'
import {
  Building2, Bus, CalendarCheck, CircleDollarSign,
  Loader2, Ticket, TrendingUp,
} from 'lucide-react'
import { getPlatformStatsRequest } from '@/lib/companies'

function money(v: number) {
  if (v >= 1_000_000) return `UGX ${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `UGX ${(v / 1_000).toFixed(0)}K`
  return `UGX ${v.toLocaleString()}`
}

function monthLabel(ym: string) {
  const [y, m] = ym.split('-')
  return new Date(Number(y), Number(m) - 1).toLocaleString('default', { month: 'short' })
}

const statusStyle: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-700',
  PENDING: 'bg-amber-100 text-amber-700',
  SUSPENDED: 'bg-rose-100 text-rose-700',
  INACTIVE: 'bg-slate-100 text-slate-500',
}

export default function HQDashboard() {
  const { data: s, isLoading } = useQuery({
    queryKey: ['platform-stats'],
    queryFn: getPlatformStatsRequest,
  })

  const topMetrics = [
    { label: 'Total Companies', value: s?.companies.total ?? '—', icon: Building2, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Platform Revenue', value: s ? money(s.totalRevenue) : '—', icon: CircleDollarSign, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: 'Total Trips', value: s?.totalTrips ?? '—', icon: CalendarCheck, color: 'text-teal-600', bg: 'bg-teal-50' },
    { label: 'Total Bookings', value: s?.totalBookings ?? '—', icon: Ticket, color: 'text-amber-600', bg: 'bg-amber-50' },
  ]

  return (
    <section className="space-y-6">
      {/* KPI cards */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {topMetrics.map(item => (
          <article key={item.label} className="card p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-500">{item.label}</p>
              <div className={`rounded-full p-2 ${item.bg}`}>
                <item.icon size={16} className={item.color} />
              </div>
            </div>
            {isLoading
              ? <Loader2 className="mt-3 animate-spin text-slate-400" size={20} />
              : <h3 className="mt-2 text-2xl font-bold text-slate-900">{item.value}</h3>
            }
          </article>
        ))}
      </div>

      {/* Revenue trend + Company status */}
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="card p-5 xl:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Platform Revenue Trend</h2>
              <p className="text-sm text-slate-500">Monthly confirmed revenue across all companies</p>
            </div>
            <TrendingUp size={18} className="text-blue-600" />
          </div>
          {isLoading
            ? <div className="mt-6 flex h-56 items-center justify-center"><Loader2 className="animate-spin text-slate-400" /></div>
            : !s || s.monthlyRevenue.length === 0
              ? <p className="mt-6 text-sm text-slate-400">No revenue data yet</p>
              : (() => {
                  const max = Math.max(...s.monthlyRevenue.map(m => m.revenue), 1)
                  return (
                    <div className="mt-6 flex h-56 items-end gap-3 rounded-2xl bg-slate-50 p-4">
                      {s.monthlyRevenue.map(item => {
                        const h = Math.max((item.revenue / max) * 100, 4)
                        return (
                          <div key={item.month} className="flex flex-1 flex-col items-center gap-2">
                            <div className="flex h-full w-full items-end">
                              <div
                                className="w-full rounded-t-xl bg-[linear-gradient(180deg,_#2563eb,_#0f766e)] shadow-sm"
                                style={{ height: `${h}%` }}
                                title={money(item.revenue)}
                              />
                            </div>
                            <p className="text-xs font-medium text-slate-500">{monthLabel(item.month)}</p>
                            <p className="text-xs font-semibold text-slate-700">{money(item.revenue)}</p>
                          </div>
                        )
                      })}
                    </div>
                  )
                })()
          }
        </div>

        <div className="card p-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="rounded-full bg-blue-100 p-2 text-blue-700"><Building2 size={16} /></div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Company Status</h2>
              <p className="text-sm text-slate-500">Registration breakdown</p>
            </div>
          </div>
          {isLoading
            ? <Loader2 className="animate-spin text-slate-400" />
            : (() => {
                const total = Math.max(s?.companies.total ?? 0, 1)
                return (
                  <div className="space-y-3">
                    {[
                      { label: 'Active', value: s?.companies.active ?? 0, bar: 'bg-emerald-500', tone: 'bg-emerald-100 text-emerald-800' },
                      { label: 'Pending', value: s?.companies.pending ?? 0, bar: 'bg-amber-400', tone: 'bg-amber-100 text-amber-800' },
                      { label: 'Suspended', value: s?.companies.suspended ?? 0, bar: 'bg-rose-400', tone: 'bg-rose-100 text-rose-800' },
                      { label: 'Inactive', value: s?.companies.inactive ?? 0, bar: 'bg-slate-300', tone: 'bg-slate-100 text-slate-600' },
                    ].map(item => (
                      <div key={item.label}>
                        <div className="mb-1 flex items-center justify-between text-sm">
                          <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${item.tone}`}>{item.label}</span>
                          <span className="font-semibold text-slate-900">{item.value}</span>
                        </div>
                        <div className="h-2 rounded-full bg-slate-100">
                          <div
                            className={`h-2 rounded-full ${item.bar}`}
                            style={{ width: `${Math.max((item.value / total) * 100, item.value > 0 ? 4 : 0)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )
              })()
          }
        </div>
      </div>

      {/* Top companies + Recent registrations */}
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="rounded-full bg-teal-100 p-2 text-teal-700"><Bus size={16} /></div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Top Companies</h2>
              <p className="text-sm text-slate-500">By booking volume</p>
            </div>
          </div>
          {isLoading
            ? <Loader2 className="animate-spin text-slate-400" />
            : !s || s.topCompanies.length === 0
              ? <p className="text-sm text-slate-400">No company data yet</p>
              : (() => {
                  const maxBookings = Math.max(...s.topCompanies.map(c => c.bookings), 1)
                  return (
                    <div className="space-y-4">
                      {s.topCompanies.map(c => (
                        <div key={c.id}>
                          <div className="mb-1 flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-slate-800">{c.name}</span>
                              <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${statusStyle[c.status] ?? 'bg-slate-100 text-slate-600'}`}>{c.status}</span>
                            </div>
                            <span className="text-slate-500">{c.bookings} bookings · {c.trips} trips · {c.buses} buses</span>
                          </div>
                          <div className="h-2.5 rounded-full bg-slate-100">
                            <div
                              className="h-2.5 rounded-full bg-[linear-gradient(90deg,_#2563eb,_#0f766e)]"
                              style={{ width: `${Math.max((c.bookings / maxBookings) * 100, c.bookings > 0 ? 4 : 0)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )
                })()
          }
        </div>

        <div className="card p-5">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Recently Registered</h2>
          {isLoading
            ? <Loader2 className="animate-spin text-slate-400" />
            : !s || s.recentCompanies.length === 0
              ? <p className="text-sm text-slate-400">No companies yet</p>
              : (
                <div className="space-y-3">
                  {s.recentCompanies.map(c => (
                    <div key={c.id} className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-800">{c.name}</p>
                        <p className="text-xs text-slate-500">{c.city} · {new Date(c.createdAt).toLocaleDateString()}</p>
                      </div>
                      <span className={`rounded-full px-2 py-1 text-xs font-semibold ${statusStyle[c.status] ?? 'bg-slate-100 text-slate-600'}`}>
                        {c.status}
                      </span>
                    </div>
                  ))}
                </div>
              )
          }
        </div>
      </div>
    </section>
  )
}
