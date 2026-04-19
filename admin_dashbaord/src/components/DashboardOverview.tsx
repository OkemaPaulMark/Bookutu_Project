const metrics = [
  {
    label: "Today's Bookings",
    value: "128",
    change: "12.5%",
    note: "from yesterday",
  },
  {
    label: "Active Buses",
    value: "24",
    change: "8.3%",
    note: "from last month",
  },
  {
    label: "Scheduled Trips",
    value: "39",
    change: "7.1%",
    note: "from last week",
  },
  {
    label: "Monthly Revenue",
    value: "UGX 18.4M",
    change: "15.8%",
    note: "from last month",
  },
];

const recentBookings = [
  {
    reference: "BK20260419A1X2",
    route: "Kampala -> Gulu",
    departure: "Apr 20, 06:30",
    status: "Confirmed",
  },
  {
    reference: "BK20260419B4F9",
    route: "Kampala -> Mbale",
    departure: "Apr 20, 08:00",
    status: "Pending",
  },
  {
    reference: "BK20260419K8M5",
    route: "Kampala -> Mbarara",
    departure: "Apr 20, 09:30",
    status: "Confirmed",
  },
];

const fleetStatus = [
  { label: "Active Buses", count: 17 },
  { label: "Maintenance Buses", count: 5 },
  { label: "Inactive Buses", count: 2 },
];

export default function DashboardOverview() {
  return (
    <section className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((item) => (
          <article key={item.label} className="card p-5">
            <p className="text-sm text-slate-500">{item.label}</p>
            <h3 className="mt-2 text-2xl font-bold">{item.value}</h3>
            <p className="mt-2 text-sm font-medium text-emerald-600">
              {item.change}
            </p>
            <p className="text-xs text-slate-500">{item.note}</p>
          </article>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Recent Bookings</h3>
            <button className="text-sm font-medium text-blue-600" type="button">
              View all
            </button>
          </div>

          <div className="space-y-3">
            {recentBookings.map((booking) => (
              <article
                key={booking.reference}
                className="rounded-lg border border-slate-200 bg-slate-50 p-3"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-slate-800">
                      {booking.reference}
                    </p>
                    <p className="text-xs text-slate-600">
                      {booking.route} • {booking.departure}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      booking.status === "Confirmed"
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-amber-100 text-amber-700"
                    }`}
                  >
                    {booking.status}
                  </span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Fleet Status</h3>
            <button className="text-sm font-medium text-blue-600" type="button">
              Manage fleet
            </button>
          </div>

          <div className="space-y-4">
            {fleetStatus.map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between border-b border-slate-100 pb-2 last:border-0"
              >
                <span className="text-sm text-slate-700">{item.label}</span>
                <span className="text-sm font-semibold text-slate-900">
                  {item.count}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
