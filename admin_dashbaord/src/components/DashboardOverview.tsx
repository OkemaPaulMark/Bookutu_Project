import { useQuery } from '@tanstack/react-query'
import {
  Bus, CalendarCheck, CircleDollarSign, Loader2,
  MapPinned, Ticket, TrendingUp, Users,
} from 'lucide-react'
import { getTripStatsRequest } from '@/lib/trips'
import { listBookingsRequest } from '@/lib/bookings'

function money(v: number) {
  if (v >= 1_000_000) return `UGX ${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `UGX ${(v / 1_000).toFixed(0)}K`
  return `UGX ${v.toLocaleString()}`
}

function monthLabel(ym: string) {
  const [y, m] = ym.split('-')
  return new Date(Number(y), Number(m) - 1).toLocaleString('default', { month: 'short' })
}

export default function DashboardOverview() {
  const statsQuery = useQuery({ queryKey: ['trip-stats'], queryFn: getTripStatsRequest })
  const bookingsQuery = useQuery({
    queryKey: ['bookings-recent'],
    queryFn: () => listBookingsRequest({ limit: 6 }),
  })

  const s = statsQuery.data
  const recentBookings = bookingsQuery.data ?? []

  const topMetrics = [
    { label: 'Total Revenue', value: s ? money(s.totalRevenue) : '—', icon: CircleDollarSign, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: 'Total Bookings', value: s?.totalBookings ?? '—', icon: Ticket, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: "Today's Trips", value: s?.todayTrips ?? '—', icon: CalendarCheck, color: 'text-teal-600', bg: 'bg-teal-50' },
    { label: 'Active Fleet', value: s ? `${s.fleet.active} buses` : '—', icon: Bus, color: 'text-amber-600', bg: 'bg-amber-50' },
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
            {statsQuery.isLoading
              ? <Loader2 className="mt-3 animate-spin text-slate-400" size={20} />
              : <h3 className="mt-2 text-2xl font-bold text-slate-900">{item.value}</h3>
            }
          </article>
        ))}
      </div>

      {/* Revenue chart + Trip status */}
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="card p-5 xl:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Revenue Trend</h2>
              <p className="text-sm text-slate-500">Monthly confirmed booking revenue</p>
            </div>
            <TrendingUp size={18} className="text-blue-600" />
          </div>
          {statsQuery.isLoading
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
            <div className="rounded-full bg-blue-100 p-2 text-blue-700"><CalendarCheck size={16} /></div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Trip Status</h2>
              <p className="text-sm text-slate-500">Operational breakdown</p>
            </div>
          </div>
          {statsQuery.isLoading
            ? <Loader2 className="animate-spin text-slate-400" />
            : (
              <div className="space-y-3">
                {[
                  { label: 'Scheduled', value: s?.scheduledTrips ?? 0, tone: 'bg-blue-100 text-blue-800' },
                  { label: 'Completed', value: s?.completedTrips ?? 0, tone: 'bg-emerald-100 text-emerald-800' },
                  { label: 'Cancelled', value: s?.cancelledTrips ?? 0, tone: 'bg-rose-100 text-rose-800' },
                  { label: "Today's", value: s?.todayTrips ?? 0, tone: 'bg-amber-100 text-amber-800' },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.tone}`}>{item.label}</span>
                    <span className="text-sm font-bold text-slate-900">{item.value}</span>
                  </div>
                ))}
              </div>
            )
          }
          <div className="mt-5 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-50 p-3 text-center">
              <p className="text-xs text-slate-500">Active Routes</p>
              <p className="mt-1 text-xl font-bold text-slate-900">{s?.activeRoutes ?? '—'}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3 text-center">
              <p className="text-xs text-slate-500">Active Drivers</p>
              <p className="mt-1 text-xl font-bold text-slate-900">{s?.activeDrivers ?? '—'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Route performance + Booking stats */}
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="card p-5 xl:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Route Performance</h2>
              <p className="text-sm text-slate-500">Revenue by route</p>
            </div>
            <MapPinned size={18} className="text-teal-600" />
          </div>
          {statsQuery.isLoading
            ? <Loader2 className="animate-spin text-slate-400" />
            : !s || s.routePerformance.length === 0
              ? <p className="text-sm text-slate-400">No route data yet</p>
              : (() => {
                  const max = Math.max(...s.routePerformance.map(r => r.revenue), 1)
                  return (
                    <div className="space-y-4">
                      {s.routePerformance.map(item => (
                        <div key={item.route}>
                          <div className="mb-1 flex items-center justify-between text-sm">
                            <span className="font-medium text-slate-800">{item.route}</span>
                            <span className="text-slate-500">{item.trips} trips · {money(item.revenue)}</span>
                          </div>
                          <div className="h-2.5 rounded-full bg-slate-100">
                            <div
                              className="h-2.5 rounded-full bg-[linear-gradient(90deg,_#2563eb,_#0f766e)]"
                              style={{ width: `${Math.max((item.revenue / max) * 100, 2)}%` }}
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
          <div className="flex items-center gap-3 mb-5">
            <div className="rounded-full bg-amber-100 p-2 text-amber-700"><Users size={16} /></div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Booking Stats</h2>
              <p className="text-sm text-slate-500">By status</p>
            </div>
          </div>
          {statsQuery.isLoading
            ? <Loader2 className="animate-spin text-slate-400" />
            : (() => {
                const total = Math.max(s?.totalBookings ?? 0, 1)
                return (
                  <div className="space-y-4">
                    {[
                      { label: 'Confirmed', value: s?.confirmedBookings ?? 0, color: 'bg-emerald-500' },
                      { label: 'Pending', value: s?.pendingBookings ?? 0, color: 'bg-amber-400' },
                      { label: 'Cancelled', value: s?.cancelledBookings ?? 0, color: 'bg-rose-400' },
                    ].map(item => (
                      <div key={item.label}>
                        <div className="mb-1 flex justify-between text-sm">
                          <span className="text-slate-700">{item.label}</span>
                          <span className="font-semibold text-slate-900">{item.value}</span>
                        </div>
                        <div className="h-2.5 rounded-full bg-slate-100">
                          <div
                            className={`h-2.5 rounded-full ${item.color}`}
                            style={{ width: `${Math.max((item.value / total) * 100, item.value > 0 ? 4 : 0)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )
              })()
          }
          <div className="mt-6 rounded-xl bg-slate-50 p-4">
            <p className="text-xs text-slate-500">Fleet Overview</p>
            <div className="mt-2 flex justify-between text-sm">
              <span className="text-emerald-700 font-medium">{s?.fleet.active ?? 0} Active</span>
              <span className="text-amber-700 font-medium">{s?.fleet.maintenance ?? 0} Maint.</span>
              <span className="text-slate-500">{s?.fleet.inactive ?? 0} Inactive</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent bookings */}
      <div className="card p-5">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Recent Bookings</h2>
        {bookingsQuery.isLoading
          ? <div className="flex items-center gap-2 text-sm text-slate-500"><Loader2 size={16} className="animate-spin" /> Loading...</div>
          : recentBookings.length === 0
            ? <p className="text-sm text-slate-400">No bookings yet</p>
            : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      <th className="pb-3 pr-4">Reference</th>
                      <th className="pb-3 pr-4">Passenger</th>
                      <th className="pb-3 pr-4">Route</th>
                      <th className="pb-3 pr-4">Date</th>
                      <th className="pb-3 pr-4">Amount</th>
                      <th className="pb-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {recentBookings.map(b => (
                      <tr key={b.id} className="hover:bg-slate-50">
                        <td className="py-3 pr-4 font-mono text-xs text-slate-700">{b.bookingReference}</td>
                        <td className="py-3 pr-4 text-slate-800">{b.passengerName}</td>
                        <td className="py-3 pr-4 text-slate-600">{b.trip.route.originCity} → {b.trip.route.destinationCity}</td>
                        <td className="py-3 pr-4 text-slate-500">{new Date(b.trip.departureDate).toLocaleDateString()}</td>
                        <td className="py-3 pr-4 font-medium text-slate-800">{money(b.totalAmount)}</td>
                        <td className="py-3">
                          <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                            b.status === 'CONFIRMED' ? 'bg-emerald-100 text-emerald-700'
                            : b.status === 'PENDING' ? 'bg-amber-100 text-amber-700'
                            : b.status === 'CANCELLED' ? 'bg-rose-100 text-rose-700'
                            : 'bg-slate-100 text-slate-700'
                          }`}>{b.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
        }
      </div>
    </section>
  )
}
