import {
  ArrowUpRight,
  Bus,
  CalendarClock,
  CircleDollarSign,
  MapPinned,
  Ticket,
  TrendingUp,
  Users,
} from "lucide-react";

const monthlyRevenue = [
  { month: "Jan", value: 18 },
  { month: "Feb", value: 24 },
  { month: "Mar", value: 22 },
  { month: "Apr", value: 31 },
  { month: "May", value: 28 },
  { month: "Jun", value: 37 },
];

const routePerformance = [
  { route: "Kampala → Masaka", trips: 42, revenue: 11800000, occupancy: 91 },
  { route: "Kampala → Jinja", trips: 38, revenue: 9400000, occupancy: 87 },
  {
    route: "Kampala → Fort Portal",
    trips: 21,
    revenue: 7850000,
    occupancy: 83,
  },
  { route: "Masaka → Mbarara", trips: 18, revenue: 5400000, occupancy: 78 },
  { route: "Jinja → Soroti", trips: 14, revenue: 4600000, occupancy: 74 },
];

const tripStatus = [
  { label: "Scheduled", value: 18, tone: "bg-blue-100 text-blue-800" },
  { label: "In progress", value: 7, tone: "bg-emerald-100 text-emerald-800" },
  { label: "Completed", value: 56, tone: "bg-slate-100 text-slate-800" },
  { label: "Cancelled", value: 4, tone: "bg-rose-100 text-rose-800" },
];

const recentActivity = [
  "UGX 1,250,000 collected from 45 confirmed seats on Kampala → Masaka.",
  "Scania K310 completed inspection and returned to active fleet status.",
  "Jinja → Soroti exceeded 80% occupancy for the third day in a row.",
  "Booking volume grew by 12% compared to last week.",
];

const weeklySeats = [
  { day: "Mon", sold: 214 },
  { day: "Tue", sold: 188 },
  { day: "Wed", sold: 236 },
  { day: "Thu", sold: 221 },
  { day: "Fri", sold: 268 },
  { day: "Sat", sold: 304 },
  { day: "Sun", sold: 192 },
];

function money(value: number) {
  return `UGX ${value.toLocaleString()}`;
}

export default function CompanyFinancialsPage() {
  const maxRevenue = Math.max(...monthlyRevenue.map((item) => item.value));
  const maxSeats = Math.max(...weeklySeats.map((item) => item.sold));

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-slate-900">Financials</h1>
        <p className="mt-1 text-sm text-slate-600">Revenue, occupancy, and route performance at a glance</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600">Monthly revenue</p>
            <CircleDollarSign size={18} className="text-emerald-600" />
          </div>
          <p className="mt-3 text-2xl font-bold text-slate-900">UGX 65.8M</p>
          <p className="mt-1 text-xs text-slate-500">+18% from last month</p>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600">Average occupancy</p>
            <TrendingUp size={18} className="text-blue-600" />
          </div>
          <p className="mt-3 text-2xl font-bold text-slate-900">86%</p>
          <p className="mt-1 text-xs text-slate-500">
            Across all scheduled trips
          </p>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600">Fleet in service</p>
            <Bus size={18} className="text-teal-600" />
          </div>
          <p className="mt-3 text-2xl font-bold text-slate-900">22 buses</p>
          <p className="mt-1 text-xs text-slate-500">
            19 active, 3 maintenance
          </p>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600">Confirmed bookings</p>
            <Ticket size={18} className="text-amber-600" />
          </div>
          <p className="mt-3 text-2xl font-bold text-slate-900">1,248</p>
          <p className="mt-1 text-xs text-slate-500">243 pending today</p>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="card p-5 xl:col-span-2">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Revenue trend
            </h2>
            <p className="text-sm text-slate-600">
              Six month snapshot in UGX millions
            </p>
          </div>

          <div className="mt-6 flex h-72 items-end gap-4 rounded-2xl bg-slate-50 p-4">
            {monthlyRevenue.map((item) => {
              const height = (item.value / maxRevenue) * 100;
              return (
                <div
                  key={item.month}
                  className="flex flex-1 flex-col items-center gap-3"
                >
                  <div className="flex h-full w-full items-end">
                    <div
                      className="w-full rounded-t-2xl bg-[linear-gradient(180deg,_#2563eb,_#0f766e)] shadow-sm"
                      style={{ height: `${height}%` }}
                    />
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-medium text-slate-500">
                      {item.month}
                    </p>
                    <p className="text-sm font-semibold text-slate-900">
                      {item.value}M
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-blue-100 p-2 text-blue-700">
              <CalendarClock size={18} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Trip status
              </h2>
              <p className="text-sm text-slate-600">Current operational mix</p>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {tripStatus.map((status) => (
              <div
                key={status.label}
                className="rounded-2xl border border-slate-200 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${status.tone}`}
                  >
                    {status.label}
                  </span>
                  <span className="text-sm font-semibold text-slate-900">
                    {status.value}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-slate-500">
              Route coverage
            </p>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              5 major routes
            </p>
            <p className="text-xs text-slate-500">
              Busy corridors across central and eastern Uganda
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="card p-5 xl:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Route performance
              </h2>
              <p className="text-sm text-slate-600">
                Revenue and occupancy by route
              </p>
            </div>
            <MapPinned size={18} className="text-teal-600" />
          </div>

          <div className="mt-5 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-slate-900">
                    Route
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-slate-900">
                    Trips
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-slate-900">
                    Revenue
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-slate-900">
                    Occupancy
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {routePerformance.map((item) => (
                  <tr key={item.route} className="transition hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">
                      {item.route}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      {item.trips}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      {money(item.revenue)}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      <div className="flex items-center gap-3">
                        <div className="h-2 w-28 rounded-full bg-slate-200">
                          <div
                            className="h-2 rounded-full bg-[linear-gradient(90deg,_#2563eb,_#0f766e)]"
                            style={{ width: `${item.occupancy}%` }}
                          />
                        </div>
                        <span className="font-medium text-slate-900">
                          {item.occupancy}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-amber-100 p-2 text-amber-700">
              <Users size={18} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Weekly seat sales
              </h2>
              <p className="text-sm text-slate-600">Seats sold per day</p>
            </div>
          </div>

          <div className="mt-5 space-y-4">
            {weeklySeats.map((item) => (
              <div key={item.day}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-700">{item.day}</span>
                  <span className="text-slate-600">{item.sold} seats</span>
                </div>
                <div className="h-3 rounded-full bg-slate-200">
                  <div
                    className="h-3 rounded-full bg-[linear-gradient(90deg,_#14b8a6,_#2563eb)]"
                    style={{ width: `${(item.sold / maxSeats) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-slate-500">
              Peak day
            </p>
            <p className="mt-2 text-2xl font-bold text-slate-900">Saturday</p>
            <p className="text-xs text-slate-500">
              304 seats sold this week
            </p>
          </div>
        </div>
      </div>

      <div className="card p-5">
        <h2 className="text-lg font-semibold text-slate-900">
          Recent insights
        </h2>
        <div className="mt-4 space-y-3">
          {recentActivity.map((item) => (
            <div
              key={item}
              className="flex items-start gap-3 rounded-2xl border border-slate-200 p-4"
            >
              <div className="mt-0.5 rounded-full bg-blue-100 p-2 text-blue-700">
                <ArrowUpRight size={16} />
              </div>
              <p className="text-sm leading-6 text-slate-700">{item}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
