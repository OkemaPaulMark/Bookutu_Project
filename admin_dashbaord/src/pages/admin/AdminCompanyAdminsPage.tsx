import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AlertCircle, CheckCircle2, Loader2, MailPlus } from "lucide-react";
import toast from "react-hot-toast";
import { getApiErrorMessage } from "@/lib/api";
import {
  createCompanyRequest,
  inviteCompanyAdminRequest,
} from "@/lib/companies";

function buildPlaceholderCompanyPayload(
  companyName: string,
  registrationNumber: string,
  adminPhoneNumber: string,
) {
  const timestamp = Date.now();
  return {
    name: companyName,
    email: `pending-${timestamp}@bookutu.local`,
    phoneNumber: adminPhoneNumber || "+256000000000",
    address: `${companyName} - details pending`,
    city: "Pending",
    state: "Pending",
    registrationNumber: registrationNumber || `PENDING-${timestamp}`,
    licenseNumber: `PENDING-${timestamp}`,
    description: "Company details will be completed by the company admin.",
    website: undefined,
    postalCode: undefined,
    taxId: undefined,
    commissionRate: undefined,
  };
}

export default function AdminCompanyAdminsPage() {
  const [companyName, setCompanyName] = useState("");
  const [registrationNumber, setRegistrationNumber] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminFirstName, setAdminFirstName] = useState("");
  const [adminLastName, setAdminLastName] = useState("");
  const [adminPhoneNumber, setAdminPhoneNumber] = useState("");

  const inviteMutation = useMutation({
    mutationFn: async () => {
      const company = await createCompanyRequest(
        buildPlaceholderCompanyPayload(
          companyName,
          registrationNumber,
          adminPhoneNumber,
        ),
      );

      return inviteCompanyAdminRequest({
        email: adminEmail,
        companyId: company.id,
        firstName: adminFirstName || undefined,
        lastName: adminLastName || undefined,
        phoneNumber: adminPhoneNumber || undefined,
      });
    },
    onSuccess: (data) => {
      toast.success(`Invite sent for ${data.invite.email}.`);
      setCompanyName("");
      setRegistrationNumber("");
      setAdminEmail("");
      setAdminFirstName("");
      setAdminLastName("");
      setAdminPhoneNumber("");
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    inviteMutation.mutate();
  }

  return (
    <section className="space-y-6">
      <h1 className="text-3xl font-semibold text-slate-900">
        Register a bus company admin
      </h1>

      <form className="card space-y-6 p-6" onSubmit={handleSubmit}>
        <div className="grid gap-5 md:grid-cols-2">
          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Company name
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              onChange={(event) => setCompanyName(event.target.value)}
              placeholder="Acme Coaches Ltd"
              required
              type="text"
              value={companyName}
            />
          </label>

          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Registration number
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              onChange={(event) => setRegistrationNumber(event.target.value)}
              placeholder="REG-123456"
              required
              type="text"
              value={registrationNumber}
            />
          </label>

          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Admin email
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              onChange={(event) => setAdminEmail(event.target.value)}
              placeholder="manager@acmecoaches.com"
              required
              type="email"
              value={adminEmail}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              First name
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              onChange={(event) => setAdminFirstName(event.target.value)}
              placeholder="Admin first name"
              type="text"
              value={adminFirstName}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Last name
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              onChange={(event) => setAdminLastName(event.target.value)}
              placeholder="Admin last name"
              type="text"
              value={adminLastName}
            />
          </label>

          <label className="block md:col-span-2">
            <span className="mb-2 block text-sm font-medium text-slate-700">
              Phone number
            </span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white"
              onChange={(event) => setAdminPhoneNumber(event.target.value)}
              placeholder="+256..."
              type="text"
              value={adminPhoneNumber}
            />
          </label>
        </div>

        <button
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-teal-300"
          disabled={inviteMutation.isPending}
          type="submit"
        >
          {inviteMutation.isPending ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <MailPlus size={18} />
          )}
          Create company and send invite
        </button>

        {inviteMutation.isError ? (
          <section className="card flex items-start gap-3 border-rose-200 bg-rose-50 p-5 text-rose-700">
            <AlertCircle size={18} className="mt-0.5" />
            <p>
              {getApiErrorMessage(
                inviteMutation.error,
                "Unable to create the company and send the invite",
              )}
            </p>
          </section>
        ) : null}

        {inviteMutation.data ? (
          <section className="card border-emerald-200 bg-emerald-50 p-5 text-emerald-900">
            <div className="flex items-start gap-3">
              <CheckCircle2 size={18} className="mt-0.5 text-emerald-600" />
              <div className="space-y-2 text-sm leading-6">
                <p>
                  {inviteMutation.data.invite.email} can now finish setup for{" "}
                  {inviteMutation.data.invite.companyName}.
                </p>
                <p>
                  The invite expires on{" "}
                  {new Date(
                    inviteMutation.data.invite.expiresAt,
                  ).toLocaleString()}
                  .
                </p>
                {inviteMutation.data.setupUrl ? (
                  <p className="break-all">
                    Development setup link:{" "}
                    <span className="font-medium">
                      {inviteMutation.data.setupUrl}
                    </span>
                  </p>
                ) : null}
              </div>
            </div>
          </section>
        ) : null}
      </form>
    </section>
  );
}
