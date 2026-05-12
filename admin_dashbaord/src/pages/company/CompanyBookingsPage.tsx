import { Eye, Download, AlertCircle, Filter } from "lucide-react";
import { useState } from "react";

interface Booking {
  id: string;
  bookingRef: string;
  passengerName: string;
  passengerPhone: string;
  from: string;
  to: string;
  departureDate: string;
  departureTime: string;
  seatNumber: string;
  price: number;
  status: "confirmed" | "pending" | "cancelled" | "completed";
  bookingDate: string;
  paymentMethod: string;
}

export default function CompanyBookingsPage() {
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const bookings: Booking[] = [
    {
      id: "1",
      bookingRef: "BK-001234",
      passengerName: "Alice Johnson",
      passengerPhone: "+256701234567",
      from: "Kampala",
      to: "Masaka",
      departureDate: "2025-05-15",
      departureTime: "08:00 AM",
      seatNumber: "A1",
      price: 25000,
      status: "confirmed",
      bookingDate: "2025-05-10",
      paymentMethod: "Mobile Money",
    },
    {
      id: "2",
      bookingRef: "BK-001235",
      passengerName: "Bob Smith",
      passengerPhone: "+256702345678",
      from: "Kampala",
      to: "Jinja",
      departureDate: "2025-05-15",
      departureTime: "10:30 AM",
      seatNumber: "B3",
      price: 18000,
      status: "confirmed",
      bookingDate: "2025-05-11",
      paymentMethod: "Card",
    },
    {
      id: "3",
      bookingRef: "BK-001236",
      passengerName: "Carol Williams",
      passengerPhone: "+256703456789",
      from: "Masaka",
      to: "Kampala",
      departureDate: "2025-05-16",
      departureTime: "07:00 AM",
      seatNumber: "C5",
      price: 25000,
      status: "pending",
      bookingDate: "2025-05-12",
      paymentMethod: "Mobile Money",
    },
    {
      id: "4",
      bookingRef: "BK-001237",
      passengerName: "David Brown",
      passengerPhone: "+256704567890",
      from: "Jinja",
      to: "Kampala",
      departureDate: "2025-05-14",
      departureTime: "02:00 PM",
      seatNumber: "D2",
      price: 18000,
      status: "completed",
      bookingDate: "2025-05-08",
      paymentMethod: "Card",
    },
    {
      id: "5",
      bookingRef: "BK-001238",
      passengerName: "Emma Davis",
      passengerPhone: "+256705678901",
      from: "Kampala",
      to: "Fort Portal",
      departureDate: "2025-05-13",
      departureTime: "11:00 AM",
      seatNumber: "E4",
      price: 45000,
      status: "cancelled",
      bookingDate: "2025-05-09",
      paymentMethod: "Mobile Money",
    },
    {
      id: "6",
      bookingRef: "BK-001239",
      passengerName: "Frank Green",
      passengerPhone: "+256706789012",
      from: "Masaka",
      to: "Mbarara",
      departureDate: "2025-05-17",
      departureTime: "06:30 AM",
      seatNumber: "F1",
      price: 35000,
      status: "confirmed",
      bookingDate: "2025-05-12",
      paymentMethod: "Card",
    },
    {
      id: "7",
      bookingRef: "BK-001240",
      passengerName: "Grace Taylor",
      passengerPhone: "+256707890123",
      from: "Jinja",
      to: "Soroti",
      departureDate: "2025-05-18",
      departureTime: "09:00 AM",
      seatNumber: "A6",
      price: 40000,
      status: "confirmed",
      bookingDate: "2025-05-12",
      paymentMethod: "Mobile Money",
    },
    {
      id: "8",
      bookingRef: "BK-001241",
      passengerName: "Henry Martinez",
      passengerPhone: "+256708901234",
      from: "Kampala",
      to: "Mbale",
      departureDate: "2025-05-19",
      departureTime: "12:00 PM",
      seatNumber: "B5",
      price: 30000,
      status: "pending",
      bookingDate: "2025-05-12",
      paymentMethod: "Card",
    },
  ];

  const filteredBookings =
    filterStatus === "all"
      ? bookings
      : bookings.filter((booking) => booking.status === filterStatus);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "bg-emerald-100 text-emerald-800";
      case "pending":
        return "bg-amber-100 text-amber-800";
      case "completed":
        return "bg-blue-100 text-blue-800";
      case "cancelled":
        return "bg-rose-100 text-rose-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  const getTotalRevenue = () => {
    return filteredBookings
      .filter((b) => b.status === "completed" || b.status === "confirmed")
      .reduce((sum, b) => sum + b.price, 0);
  };

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Bookings</h1>
          <p className="mt-1 text-sm text-slate-600">
            Manage and track all passenger bookings
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="card p-4">
          <p className="text-sm text-slate-600">Total Bookings</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {bookings.length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Confirmed</p>
          <p className="mt-2 text-2xl font-bold text-emerald-600">
            {bookings.filter((b) => b.status === "confirmed").length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Pending</p>
          <p className="mt-2 text-2xl font-bold text-amber-600">
            {bookings.filter((b) => b.status === "pending").length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Revenue</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            UGX {getTotalRevenue().toLocaleString()}
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <Filter size={18} className="text-slate-600" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-blue-500"
          >
            <option value="all">All Bookings</option>
            <option value="confirmed">Confirmed</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <span className="text-sm text-slate-600">
            Showing {filteredBookings.length} bookings
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Booking Ref
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Passenger
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Route
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Seat
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Payment
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredBookings.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <AlertCircle size={32} className="text-slate-400" />
                      <p className="text-slate-600">No bookings found</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredBookings.map((booking) => (
                  <tr key={booking.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-3 text-sm font-medium text-blue-600">
                      {booking.bookingRef}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <div>
                        <p className="font-medium text-slate-900">
                          {booking.passengerName}
                        </p>
                        <p className="text-xs text-slate-500">
                          {booking.passengerPhone}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      <div className="flex items-center gap-2">
                        <span>{booking.from}</span>
                        <span className="text-slate-400">→</span>
                        <span>{booking.to}</span>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      <div>
                        <p>
                          {new Date(booking.departureDate).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-slate-500">
                          {booking.departureTime}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-sm font-medium text-slate-900">
                      {booking.seatNumber}
                    </td>
                    <td className="px-6 py-3 text-sm font-semibold text-slate-900">
                      UGX {booking.price.toLocaleString()}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <span
                        className={`inline-block rounded-full px-3 py-1 text-xs font-semibold capitalize ${getStatusColor(booking.status)}`}
                      >
                        {booking.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {booking.paymentMethod}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded transition"
                          title="View details"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          className="p-1.5 text-slate-600 hover:text-emerald-600 hover:bg-emerald-50 rounded transition"
                          title="Download receipt"
                        >
                          <Download size={16} />
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

      {/* Footer Info */}
      <div className="card p-4">
        <p className="text-xs text-slate-600">
          Data from mobile app bookings • Last updated: Today at{" "}
          {new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </section>
  );
}
