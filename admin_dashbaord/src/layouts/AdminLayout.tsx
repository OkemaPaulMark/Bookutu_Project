import { useEffect, useRef, useState } from "react";
import {
  Bell,
  Building2,
  CalendarClock,
  ChevronDown,
  CircleDollarSign,
  Cog,
  KeyRound,
  LogOut,
  Megaphone,
  Search,
  Shield,
  Ticket,
  UserCircle2,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@store/authStore";

const navItems = [
  { to: "/admin", label: "Dashboard", icon: CalendarClock },
  {
    to: "/admin/company-admins",
    label: "Register Company Admin",
    icon: KeyRound,
  },
  { to: "/admin/companies", label: "Companies", icon: Building2 },
  { to: "/admin/bookings", label: "Bookings", icon: Ticket },
  { to: "/admin/financials", label: "Financials", icon: CircleDollarSign },
  { to: "/admin/adverts", label: "Adverts", icon: Megaphone },
  { to: "/admin/settings", label: "Settings", icon: Cog },
];

export default function AdminLayout() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (!menuRef.current) return;
      if (!menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleLogout() {
    setMenuOpen(false);
    logout();
    navigate("/login");
  }

  // Use a static navbar title instead of page-specific dynamic titles
  // const title = "Dashboard";

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="sidebar-width fixed inset-y-0 left-0 border-r border-slate-200 bg-white shadow-sm">
        <div className="flex items-center border-b border-slate-200 p-5">
          <div className="rounded bg-blue-600 p-2 text-white">
            <Shield size={14} />
          </div>
          <h1 className="menu-text ml-3 text-xl font-bold truncate">
            {user?.companyName || "Bookutu HQ"}
          </h1>
        </div>

        <nav className="space-y-2 p-4">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/admin"}
              className={({ isActive }) =>
                `flex items-center rounded-lg px-3 py-3 text-sm font-medium ${
                  isActive
                    ? "bg-blue-100 text-blue-700"
                    : "text-slate-700 hover:bg-slate-100"
                }`
              }
            >
              <Icon size={18} />
              <span className="menu-text ml-3">{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="main-offset">
        <header className="border-b border-slate-200 bg-white">
          <div className="flex items-center justify-between p-4">
            {/* Left side: Search */}
            <div className="hidden items-center gap-4 md:flex flex-1">
              <div className="relative w-80">
                <Search
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                />
                <input
                  className="w-full rounded-md border border-slate-300 py-2.5 pl-9 pr-3 text-sm"
                  placeholder="Search..."
                  type="text"
                />
              </div>
            </div>

            {/* Right side: Notification and User Menu */}
            <div className="flex items-center gap-4">
              <button
                className="rounded-full p-2 text-slate-600 hover:bg-slate-100"
                type="button"
              >
                <Bell size={18} />
              </button>

              <div className="relative" ref={menuRef}>
                <button
                  className="flex items-center rounded-lg border border-slate-200 bg-white px-3 py-1.5 hover:bg-slate-50"
                  onClick={() => setMenuOpen((open) => !open)}
                  type="button"
                >
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-blue-700">
                    <UserCircle2 size={18} />
                  </div>
                  <div className="ml-2 text-left">
                    <p className="max-w-[180px] truncate text-sm font-medium">
                      {user?.name}
                    </p>
                    <p className="max-w-[180px] truncate text-xs text-slate-500">
                      {user?.email}
                    </p>
                  </div>
                  <ChevronDown size={16} className="ml-2 text-slate-500" />
                </button>

                {menuOpen ? (
                  <div className="absolute right-0 top-12 z-40 w-48 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                    <button
                      className="flex w-full items-center px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                      onClick={() => {
                        setMenuOpen(false);
                        navigate("/admin/settings");
                      }}
                      type="button"
                    >
                      <Cog size={15} className="mr-2" />
                      Edit profile
                    </button>
                    <button
                      className="flex w-full items-center px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50"
                      onClick={handleLogout}
                      type="button"
                    >
                      <LogOut size={15} className="mr-2" />
                      Logout
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </header>
        <section className="p-6">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
