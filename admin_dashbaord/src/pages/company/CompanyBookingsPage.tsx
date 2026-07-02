import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, AlertCircle, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import { listBookingsRequest, cancelBookingRequest, type BookingRecord } from '@/lib/bookings'
import { getApiErrorMessage } from '@/lib/api'

const STATUS_COLORS: Record<string, string> = {
  CONFIRMED: 'bg-emerald-100 text-emerald-800',
  PENDING: 'bg-amber-100 text-amber-800',
  COMPLETED: 'bg-blue-100 text-blue-800',
  CANCELLED: 'bg-rose-100 text-rose-800',
  NO_SHOW: 'bg-slate-100 text-slate-700'
}

export default function CompanyBookingsPage() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')

  const bookingsQuery = useQuery({
    queryKey: ['bookings', statusFilter, search],
    queryFn: () => listBookingsRequest({ status: statusFilter || undefined, search: search || undefined })
  })

  const cancelMutation = useMutation({
    mutationFn: cancelBookingRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['bookings'] }); toast.success('Booking cancelled') },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to cancel booking'))
  })

  const bookings = bookingsQuery.data ?? []

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-slate-900">Bookings</h1>
        <p className="mt-1 text-sm text-slate-600">Manage and track all passenger bookings</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="card p-4"><p className="text-sm text-slate-600">Total</p><p className="mt-2 text-2xl font-bold text-slate-900">{bookings.length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Confirmed</p><p className="mt-2 text-2xl font-bold text-emerald-600">{bookings.filter(b => b.status === 'CONFIRMED').length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Pending</p><p className="mt-2 text-2xl font-bold text-amber-600">{bookings.filter(b => b.status === 'PENDING').length}</p></div>
        <div className="card p-4"><p className="text-sm text-slate-600">Revenue</p><p className="mt-2 text-2xl font-bold text-slate-900">UGX {bookings.filter(b => ['CONFIRMED', 'COMPLETED'].includes(b.status)).reduce((s, b) => s + Number(b.totalAmount), 0).toLocaleString()}</p></div>
      </div>

      <div className="card flex flex-wrap items-center gap-4 p-4">
        <Filter size={18} className="text-slate-500" />
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500">
          <option value="">All Statuses</option>
          {['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name, phone, ref..." className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 w-64" />
        {bookingsQuery.isFetching && <Loader2 size={16} className="animate-spin text-slate-400" />}
      </div>

      {bookingsQuery.isLoading && <div className="card flex items-center gap-3 p-6 text-slate-600"><Loader2 className="animate-spin" size={18} /> Loading bookings...</div>}
      {bookingsQuery.isError && <div className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700"><AlertCircle size={18} className="mt-0.5" />{getApiErrorMessage(bookingsQuery.error)}</div>}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Ref', 'Passenger', 'Route', 'Date', 'Seat', 'Amount', 'Status', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-sm font-semibold text-slate-900">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {bookings.length === 0 && !bookingsQuery.isLoading ? (
                <tr><td colSpan={8} className="px-6 py-8 text-center text-slate-500">No bookings found</td></tr>
              ) : bookings.map((booking: BookingRecord) => (
                <tr key={booking.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-3 text-sm font-medium text-blue-600">{booking.bookingReference}</td>
                  <td className="px-6 py-3 text-sm">
                    <p className="font-medium text-slate-900">{booking.passengerName}</p>
                    <p className="text-xs text-slate-500">{booking.passengerPhone}</p>
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-600">{booking.trip.route.originCity} → {booking.trip.route.destinationCity}</td>
                  <td className="px-6 py-3 text-sm text-slate-600">
                    <p>{new Date(booking.trip.departureDate).toLocaleDateString()}</p>
                    <p className="text-xs text-slate-400">{booking.trip.departureTime}</p>
                  </td>
                  <td className="px-6 py-3 text-sm font-medium text-slate-900">{booking.seat.seatNumber}</td>
                  <td className="px-6 py-3 text-sm font-semibold text-slate-900">UGX {Number(booking.totalAmount).toLocaleString()}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[booking.status] ?? 'bg-slate-100 text-slate-800'}`}>{booking.status}</span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    {['PENDING', 'CONFIRMED'].includes(booking.status) && (
                      <button onClick={() => cancelMutation.mutate(booking.id)} disabled={cancelMutation.isPending} className="rounded px-2 py-1 text-xs font-medium text-rose-700 hover:bg-rose-50 transition disabled:opacity-50">
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
