import { FormEvent, useState } from "react";
import {
  Eye,
  Edit2,
  Trash2,
  Plus,
  X,
  Loader2,
  AlertCircle,
} from "lucide-react";
import toast from "react-hot-toast";

interface Trip {
  id: string;
  tripRef: string;
  route: string;
  bus: string;
  driver: string;
  departureDate: string;
  departureTime: string;
  seatsBooked: number;
  totalSeats: number;
  fare: number;
  status: "scheduled" | "in-progress" | "completed" | "cancelled";
  revenue: number;
}

export default function CompanyTripsPage() {
  const [showModal, setShowModal] = useState(false);
  const [trips, setTrips] = useState<Trip[]>([
    {
      id: "1",
      tripRef: "TRIP-001",
      route: "Kampala - Masaka",
      bus: "UBK-001",
      driver: "John Doe",
      departureDate: "2025-05-15",
      departureTime: "08:00 AM",
      seatsBooked: 45,
      totalSeats: 50,
      fare: 25000,
      status: "scheduled",
      revenue: 1125000,
    },
    {
      id: "2",
      tripRef: "TRIP-002",
      route: "Kampala - Jinja",
      bus: "UBK-002",
      driver: "Jane Smith",
      departureDate: "2025-05-15",
      departureTime: "10:30 AM",
      seatsBooked: 40,
      totalSeats: 45,
      fare: 18000,
      status: "scheduled",
      revenue: 720000,
    },
    {
      id: "3",
      tripRef: "TRIP-003",
      route: "Kampala - Fort Portal",
      bus: "UBK-004",
      driver: "Peter Johnson",
      departureDate: "2025-05-14",
      departureTime: "02:00 PM",
      seatsBooked: 48,
      totalSeats: 50,
      fare: 45000,
      status: "completed",
      revenue: 2160000,
    },
    {
      id: "4",
      tripRef: "TRIP-004",
      route: "Masaka - Mbarara",
      bus: "UBK-001",
      driver: "Grace Lee",
      departureDate: "2025-05-16",
      departureTime: "06:00 AM",
      seatsBooked: 25,
      totalSeats: 50,
      fare: 35000,
      status: "scheduled",
      revenue: 875000,
    },
    {
      id: "5",
      tripRef: "TRIP-005",
      route: "Jinja - Soroti",
      bus: "UBK-002",
      driver: "David Brown",
      departureDate: "2025-05-14",
      departureTime: "09:00 AM",
      seatsBooked: 42,
      totalSeats: 45,
      fare: 40000,
      status: "in-progress",
      revenue: 1680000,
    },
    {
      id: "6",
      tripRef: "TRIP-006",
      route: "Kampala - Masaka",
      bus: "UBK-004",
      driver: "Emma Wilson",
      departureDate: "2025-05-13",
      departureTime: "11:00 AM",
      seatsBooked: 0,
      totalSeats: 50,
      fare: 25000,
      status: "cancelled",
      revenue: 0,
    },
  ]);

  const [formData, setFormData] = useState({
    route: "",
    bus: "",
    driver: "",
    departureDate: "",
    departureTime: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleInputChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newTrip: Trip = {
        id: Date.now().toString(),
        tripRef: `TRIP-${String(trips.length + 1).padStart(3, "0")}`,
        route: formData.route,
        bus: formData.bus,
        driver: formData.driver,
        departureDate: formData.departureDate,
        departureTime: formData.departureTime,
        seatsBooked: 0,
        totalSeats: 50,
        fare: 25000,
        status: "scheduled",
        revenue: 0,
      };

      setTrips((prev) => [newTrip, ...prev]);
      toast.success("Trip scheduled successfully");

      setFormData({
        route: "",
        bus: "",
        driver: "",
        departureDate: "",
        departureTime: "",
      });

      setShowModal(false);
      setIsSubmitting(false);
    }, 1000);
  }

  function handleDelete(id: string) {
    if (confirm("Are you sure you want to cancel this trip?")) {
      setTrips((prev) =>
        prev.map((trip) =>
          trip.id === id ? { ...trip, status: "cancelled" as const } : trip,
        ),
      );
      toast.success("Trip cancelled");
    }
  }

  function handleView(trip: Trip) {
    toast.success(`Viewing ${trip.tripRef}`);
  }

  function handleEdit(trip: Trip) {
    setFormData({
      route: trip.route,
      bus: trip.bus,
      driver: trip.driver,
      departureDate: trip.departureDate,
      departureTime: trip.departureTime,
    });
    setShowModal(true);
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "bg-blue-100 text-blue-800";
      case "in-progress":
        return "bg-emerald-100 text-emerald-800";
      case "completed":
        return "bg-slate-100 text-slate-800";
      case "cancelled":
        return "bg-rose-100 text-rose-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  const occupancyRate = (booked: number, total: number) => {
    return Math.round((booked / total) * 100);
  };

  const totalRevenue = trips
    .filter((t) => t.status === "completed" || t.status === "in-progress")
    .reduce((sum, t) => sum + t.revenue, 0);

  const scheduledTrips = trips.filter((t) => t.status === "scheduled").length;
  const completedTrips = trips.filter((t) => t.status === "completed").length;

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Trips</h1>
          <p className="mt-1 text-sm text-slate-600">
            Schedule and manage bus trips
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          Schedule Trip
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="card p-4">
          <p className="text-sm text-slate-600">Total Trips</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {trips.length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Scheduled</p>
          <p className="mt-2 text-2xl font-bold text-blue-600">
            {scheduledTrips}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Completed</p>
          <p className="mt-2 text-2xl font-bold text-emerald-600">
            {completedTrips}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Revenue</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            UGX {totalRevenue.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Trip Ref
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Route
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Bus
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Driver
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Occupancy
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Revenue
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {trips.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <AlertCircle size={32} className="text-slate-400" />
                      <p className="text-slate-600">No trips scheduled yet</p>
                    </div>
                  </td>
                </tr>
              ) : (
                trips.map((trip) => (
                  <tr key={trip.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-3 text-sm font-medium text-blue-600">
                      {trip.tripRef}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-900">
                      {trip.route}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {trip.bus}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {trip.driver}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      <div>
                        <p>
                          {new Date(trip.departureDate).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-slate-500">
                          {trip.departureTime}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <div>
                        <p className="font-medium text-slate-900">
                          {trip.seatsBooked}/{trip.totalSeats}
                        </p>
                        <div className="mt-1 w-20 bg-slate-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{
                              width: `${occupancyRate(trip.seatsBooked, trip.totalSeats)}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-sm font-semibold text-slate-900">
                      UGX {trip.revenue.toLocaleString()}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <span
                        className={`inline-block rounded-full px-3 py-1 text-xs font-semibold capitalize ${getStatusColor(trip.status)}`}
                      >
                        {trip.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleView(trip)}
                          className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded transition"
                          title="View"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => handleEdit(trip)}
                          disabled={trip.status !== "scheduled"}
                          className="p-1.5 text-slate-600 hover:text-amber-600 hover:bg-amber-50 rounded transition disabled:opacity-50"
                          title="Edit"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(trip.id)}
                          disabled={trip.status === "cancelled"}
                          className="p-1.5 text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded transition disabled:opacity-50"
                          title="Cancel"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card max-h-[90vh] w-full max-w-md overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900">
                Schedule Trip
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-500 hover:text-slate-700 transition"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <form onSubmit={handleSubmit} className="space-y-5 p-6">
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Route
                </span>
                <select
                  name="route"
                  value={formData.route}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  required
                >
                  <option value="">Select Route</option>
                  <option value="Kampala - Masaka">Kampala - Masaka</option>
                  <option value="Kampala - Jinja">Kampala - Jinja</option>
                  <option value="Kampala - Fort Portal">
                    Kampala - Fort Portal
                  </option>
                  <option value="Masaka - Mbarara">Masaka - Mbarara</option>
                  <option value="Jinja - Soroti">Jinja - Soroti</option>
                </select>
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Bus
                </span>
                <select
                  name="bus"
                  value={formData.bus}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  required
                >
                  <option value="">Select Bus</option>
                  <option value="UBK-001">UBK-001 (Scania K310)</option>
                  <option value="UBK-002">UBK-002 (Volvo B9R)</option>
                  <option value="UBK-004">UBK-004 (Scania K420)</option>
                </select>
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Driver
                </span>
                <select
                  name="driver"
                  value={formData.driver}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  required
                >
                  <option value="">Select Driver</option>
                  <option value="John Doe">John Doe</option>
                  <option value="Jane Smith">Jane Smith</option>
                  <option value="Peter Johnson">Peter Johnson</option>
                  <option value="Grace Lee">Grace Lee</option>
                  <option value="David Brown">David Brown</option>
                </select>
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Departure Date
                </span>
                <input
                  type="date"
                  name="departureDate"
                  value={formData.departureDate}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Departure Time
                </span>
                <input
                  type="time"
                  name="departureTime"
                  value={formData.departureTime}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  required
                />
              </label>

              {/* Modal Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 rounded-lg border border-slate-200 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Scheduling...
                    </>
                  ) : (
                    "Schedule Trip"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
