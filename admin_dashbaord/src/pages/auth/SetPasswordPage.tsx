import { FormEvent, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Loader2, LockKeyhole } from "lucide-react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { fetchPasswordSetupDetails } from "@/lib/auth";
import { getApiErrorMessage } from "@/lib/api";
import { useAuthStore } from "@store/authStore";

export default function SetPasswordPage() {
  const user = useAuthStore((state) => state.user);
  const completePasswordSetup = useAuthStore(
    (state) => state.completePasswordSetup,
  );
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get("token") ?? "", [searchParams]);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const inviteQuery = useQuery({
    queryKey: ["password-setup", token],
    queryFn: () => fetchPasswordSetupDetails(token),
    enabled: Boolean(token),
  });

  // Allow rendering the password setup page when a valid token is present
  // even if another user is currently logged in. If no token is provided
  // and the user is logged in, redirect to their dashboard as before.
  if (user && !token) {
    return (
      <Navigate
        to={user.role === "SUPER_ADMIN" ? "/admin" : "/company"}
        replace
      />
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      const nextUser = await completePasswordSetup({
        token,
        firstName,
        lastName,
        phoneNumber: phoneNumber || undefined,
        password,
        confirmPassword,
      });

      toast.success("Your password has been set. You can start working now.");
      navigate(nextUser.role === "SUPER_ADMIN" ? "/admin" : "/company");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Unable to finish account setup"));
    } finally {
      setSubmitting(false);
    }
  }

  const invite = inviteQuery.data;
  const hasInviteError = inviteQuery.isError || !token;

  useEffect(() => {
    if (!invite) return;
    setFirstName(invite.firstName ?? "");
    setLastName(invite.lastName ?? "");
    setPhoneNumber(invite.phoneNumber ?? "");
  }, [invite]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-10">
      <section className="w-full max-w-lg rounded-[28px] border border-white/10 bg-slate-900/90 p-8 text-white shadow-2xl shadow-black/30 backdrop-blur">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-500/15 text-teal-300 ring-1 ring-teal-400/20">
          <LockKeyhole size={22} />
        </div>

        <div className="mt-6">
          <p className="text-sm uppercase tracking-[0.2em] text-teal-200">
            Account setup
          </p>
          <h1 className="mt-3 text-3xl font-semibold">
            Set your dashboard password
          </h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Finish your Bookutu company admin access and sign in from the same
            dashboard afterwards.
          </p>
        </div>

        {inviteQuery.isLoading ? (
          <div className="mt-8 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-slate-200">
            <Loader2 className="animate-spin" size={18} />
            Checking your invitation link...
          </div>
        ) : null}

        {hasInviteError ? (
          <div className="mt-8 rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-4 text-sm leading-6 text-rose-100">
            This password setup link is invalid or has expired. Ask Bookutu
            admin to send a new company admin invite.
          </div>
        ) : null}

        {invite ? (
          <>
            <div className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-300">
                {invite.companyName ?? "Bookutu company dashboard"}
              </p>
              <p className="mt-1 text-base font-semibold">{invite.email}</p>
            </div>

            <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm text-slate-200">
                    First name
                  </span>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-teal-400"
                    onChange={(event) => setFirstName(event.target.value)}
                    placeholder="First name"
                    required
                    type="text"
                    value={firstName}
                  />
                </label>
                <label className="block">
                  <span className="mb-2 block text-sm text-slate-200">
                    Last name
                  </span>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-teal-400"
                    onChange={(event) => setLastName(event.target.value)}
                    placeholder="Last name"
                    required
                    type="text"
                    value={lastName}
                  />
                </label>
              </div>

              <label className="block">
                <span className="mb-2 block text-sm text-slate-200">
                  Phone number
                </span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-teal-400"
                  onChange={(event) => setPhoneNumber(event.target.value)}
                  placeholder="+256..."
                  type="text"
                  value={phoneNumber}
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm text-slate-200">
                  Password
                </span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-teal-400"
                  minLength={8}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="At least 8 characters"
                  required
                  type="password"
                  value={password}
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm text-slate-200">
                  Confirm password
                </span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-teal-400"
                  minLength={8}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Repeat the password"
                  required
                  type="password"
                  value={confirmPassword}
                />
              </label>

              <button
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-teal-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-teal-400 disabled:cursor-not-allowed disabled:bg-teal-300"
                disabled={submitting}
                type="submit"
              >
                {submitting ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : null}
                Finish account setup
              </button>
            </form>
          </>
        ) : null}
      </section>
    </main>
  );
}
