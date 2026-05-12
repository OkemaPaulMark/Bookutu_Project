import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, Building2, Loader2, Save } from "lucide-react";
import toast from "react-hot-toast";
import { getApiErrorMessage } from "@/lib/api";
import { getCompanyRequest, updateCompanyRequest } from "@/lib/companies";
import { useAuthStore } from "@store/authStore";

export default function CompanySettingsPage() {
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  const companyId = user?.companyId ?? "";

  const companyQuery = useQuery({
    queryKey: ["company", companyId],
    queryFn: () => getCompanyRequest(companyId),
    enabled: Boolean(companyId),
  });

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [registrationNumber, setRegistrationNumber] = useState("");
  const [licenseNumber, setLicenseNumber] = useState("");

  useEffect(() => {
    if (!companyQuery.data) return;
    setName(companyQuery.data.name ?? "");
    setEmail(companyQuery.data.email ?? "");
    setPhoneNumber(companyQuery.data.phoneNumber ?? "");
    setAddress(companyQuery.data.address ?? "");
    setCity(companyQuery.data.city ?? "");
    setState(companyQuery.data.state ?? "");
    setRegistrationNumber(companyQuery.data.registrationNumber ?? "");
    setLicenseNumber(companyQuery.data.licenseNumber ?? "");
  }, [companyQuery.data]);

  const updateMutation = useMutation({
    mutationFn: () =>
      updateCompanyRequest(companyId, {
        name,
        email,
        phoneNumber,
        address,
        city,
        state,
        registrationNumber,
        licenseNumber,
      }),
    onSuccess: async () => {
      toast.success("Company details saved.");
      await queryClient.invalidateQueries({ queryKey: ["company", companyId] });
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    updateMutation.mutate();
  }

  if (!companyId) {
    return (
      <section className="card flex items-start gap-3 p-6 text-slate-600">
        <AlertCircle size={18} className="mt-0.5" />
        <p>No company is attached to this account yet.</p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <header className="rounded-3xl bg-[linear-gradient(135deg,_#0f172a,_#134e4a)] p-6 text-white shadow-lg shadow-slate-900/10">
        <p className="text-sm uppercase tracking-[0.16em] text-teal-200">
          Company profile
        </p>
        <h1 className="mt-3 text-3xl font-semibold">
          Complete your company details
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-200">
          Finish setting up the company profile after the super admin creates
          your account.
        </p>
      </header>

      <form className="card space-y-6 p-6" onSubmit={handleSubmit}>
        <div className="grid gap-5 md:grid-cols-2">
          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Company name
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </label>

          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Company email
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Phone number
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={phoneNumber}
              onChange={(event) => setPhoneNumber(event.target.value)}
            />
          </label>

          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Address
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              City
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={city}
              onChange={(event) => setCity(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              State / region
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={state}
              onChange={(event) => setState(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Registration number
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={registrationNumber}
              onChange={(event) => setRegistrationNumber(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              License number
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              value={licenseNumber}
              onChange={(event) => setLicenseNumber(event.target.value)}
            />
          </label>
        </div>

        <button
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-teal-300"
          disabled={updateMutation.isPending || companyQuery.isLoading}
          type="submit"
        >
          {updateMutation.isPending ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <Save size={18} />
          )}
          Save company details
        </button>

        {companyQuery.isError ? (
          <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-5 text-rose-700">
            <AlertCircle size={18} className="mt-0.5" />
            <p>
              {getApiErrorMessage(
                companyQuery.error,
                "Unable to load company details",
              )}
            </p>
          </section>
        ) : null}

        {updateMutation.isError ? (
          <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-5 text-rose-700">
            <AlertCircle size={18} className="mt-0.5" />
            <p>
              {getApiErrorMessage(
                updateMutation.error,
                "Unable to save company details",
              )}
            </p>
          </section>
        ) : null}

        {companyQuery.data ? (
          <section className="card flex items-start gap-3 border-slate-200 bg-slate-50 p-5 text-slate-700">
            <Building2 size={18} className="mt-0.5 text-teal-700" />
            <p>Complete company details are editable from this page.</p>
          </section>
        ) : null}
      </form>
    </section>
  );
}
