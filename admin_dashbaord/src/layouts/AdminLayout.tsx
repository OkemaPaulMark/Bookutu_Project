import { useEffect, useRef, useState } from "react";
import {
  Bell,
  Building2,
  CalendarClock,
  ChevronDown,
  CircleDollarSign,
  Cog,
  LogOut,
  Megaphone,
  Search,
  Shield,
  Smartphone,
  Ticket,
  UserCircle2,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@store/authStore";

const navItems = [
  { to: "/admin", label: "Dashboard", icon: CalendarClock },
  { to: "/admin/companies", label: "Companies", icon: Building2 },
  { to: "/admin/passengers", label: "Passengers", icon: Smartphone },
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
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
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

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Full-width topnav */}
      <header className="topnav-height fixed inset-x-0 top-0 z-30 flex items-center justify-between border-b border-slate-200 bg-white px-5 shadow-sm">
        {/* Left: brand */}
        <div className="flex items-center gap-3">
          <div className="rounded bg-blue-600 p-1.5 text-white">
            <Shield size={16} />
          </div>
          <span className="text-base font-bold text-slate-900">
            Bookutu HQ
          </span>
        </div>

        {/* Centre: search */}
        <div className="hidden md:flex flex-1 justify-center px-8">
          <div className="relative w-80">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none focus:border-blue-400 focus:bg-white"
              placeholder="Search..."
              type="text"
            />
          </div>
        </div>

        {/* Right: bell + user menu */}
        <div className="flex items-center gap-3">
          <button className="rounded-full p-2 text-slate-500 hover:bg-slate-100" type="button">
            <Bell size={18} />
          </button>

          <div className="relative" ref={menuRef}>
            <button
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 hover:bg-slate-50"
              onClick={() => setMenuOpen((o) => !o)}
              type="button"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-700">
                <UserCircle2 size={17} />
              </div>
              <div className="hidden text-left md:block">
                <p className="max-w-[140px] truncate text-sm font-medium leading-tight">{user?.name}</p>
                <p className="max-w-[140px] truncate text-xs text-slate-500">{user?.email}</p>
              </div>
              <ChevronDown size={15} className="text-slate-400" />
            </button>

            {menuOpen && (
              <div className="absolute right-0 top-11 z-40 w-48 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                <button
                  className="flex w-full items-center px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                  onClick={() => { setMenuOpen(false); navigate("/admin/settings"); }}
                  type="button"
                >
                  <Cog size={15} className="mr-2" /> Edit profile
                </button>
                <button
                  className="flex w-full items-center px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50"
                  onClick={handleLogout}
                  type="button"
                >
                  <LogOut size={15} className="mr-2" /> Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Sidebar — starts below topnav */}
      <aside className="sidebar-width fixed bottom-0 left-0 top-[68px] z-20 border-r border-slate-200 bg-white shadow-sm overflow-y-auto">
        <nav className="space-y-1 p-3">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/admin"}
              className={({ isActive }) =>
                `flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-100 text-blue-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`
              }
            >
              <Icon size={18} />
              <span className="menu-text ml-3">{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="main-offset">
        <section className="p-6">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
