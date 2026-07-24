import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, AlertCircle, Filter, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { listBookingsRequest, deleteBookingRequest, type BookingRecord } from '@/lib/bookings'
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

  const deleteMutation = useMutation({
    mutationFn: deleteBookingRequest,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['bookings'] }); toast.success('Booking deleted') },
    onError: (e) => toast.error(getApiErrorMessage(e, 'Failed to delete booking'))
  })

  function handleDelete(booking: BookingRecord) {
    if (window.confirm(`Delete booking ${booking.bookingReference}? This cannot be undone.`)) {
      deleteMutation.mutate(booking.id)
    }
  }

  const bookings = bookingsQuery.data ?? []

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-slate-900">Bookings</h1>
        <p className="mt-1 text-sm text-slate-600">Manage and track all passenger bookings</p>
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
                    {new Date(booking.createdAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}, {new Date(booking.createdAt).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-6 py-3 text-sm font-medium text-slate-900">{booking.seat.seatNumber}</td>
                  <td className="px-6 py-3 text-sm font-semibold text-slate-900">UGX {Number(booking.totalAmount).toLocaleString()}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[booking.status] ?? 'bg-slate-100 text-slate-800'}`}>{booking.status}</span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <button onClick={() => handleDelete(booking)} disabled={deleteMutation.isPending} title="Delete" className="rounded p-1.5 text-rose-700 hover:bg-rose-50 transition disabled:opacity-50">
                      <Trash2 size={15} />
                    </button>
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
