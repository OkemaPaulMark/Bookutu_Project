import { useQuery } from '@tanstack/react-query'
import { AlertCircle, Building2, Loader2 } from 'lucide-react'
import { listCompaniesRequest } from '@/lib/companies'
import { getApiErrorMessage } from '@/lib/api'

export default function AdminCompaniesPage() {
  const companiesQuery = useQuery({
    queryKey: ['companies'],
    queryFn: listCompaniesRequest
  })

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-teal-700">Directory</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">Bus companies on Bookutu</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            Review operators, their current status, and the contact details Bookutu uses for onboarding and support.
          </p>
        </div>
        <div className="rounded-2xl bg-slate-950 px-4 py-3 text-sm text-white">
          {companiesQuery.data?.length ?? 0} companies
        </div>
      </header>

      {companiesQuery.isLoading ? (
        <section className="card flex items-center gap-3 p-6 text-slate-600">
          <Loader2 className="animate-spin" size={18} />
          Loading companies...
        </section>
      ) : null}

      {companiesQuery.isError ? (
        <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-6 text-rose-700">
          <AlertCircle size={18} className="mt-0.5" />
          <p>{getApiErrorMessage(companiesQuery.error, 'Unable to load companies')}</p>
        </section>
      ) : null}

      {companiesQuery.data?.length ? (
        <section className="grid gap-4 xl:grid-cols-2">
          {companiesQuery.data.map((company) => (
            <article key={company.id} className="card p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-2xl bg-teal-50 p-3 text-teal-700">
                      <Building2 size={18} />
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">{company.name}</h2>
                      <p className="text-sm text-slate-500">{company.city}, {company.state}</p>
                    </div>
                  </div>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    company.status === 'ACTIVE'
                      ? 'bg-emerald-100 text-emerald-700'
                      : company.status === 'PENDING'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {company.status}
                </span>
              </div>

              <dl className="mt-5 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
                <div>
                  <dt className="text-slate-400">Company email</dt>
                  <dd className="mt-1 font-medium text-slate-800">{company.email}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Phone</dt>
                  <dd className="mt-1 font-medium text-slate-800">{company.phoneNumber}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Registration</dt>
                  <dd className="mt-1 font-medium text-slate-800">{company.registrationNumber}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Joined</dt>
                  <dd className="mt-1 font-medium text-slate-800">
                    {new Date(company.createdAt).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </article>
          ))}
        </section>
      ) : null}
    </section>
  )
}
