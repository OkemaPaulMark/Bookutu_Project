import { Navigate, Route, Routes } from "react-router-dom";
import RoleRoute from "@components/RoleRoute";
import AdminLayout from "@layouts/AdminLayout";
import CompanyLayout from "@layouts/CompanyLayout";
import LoginPage from "@pages/auth/LoginPage";
import AdminOverviewPage from "@pages/admin/AdminOverviewPage";
import AdminCompaniesPage from "@pages/admin/AdminCompaniesPage";
import AdminBookingsPage from "@pages/admin/AdminBookingsPage";
import AdminFinancialsPage from "@pages/admin/AdminFinancialsPage";
import AdminAdvertsPage from "@pages/admin/AdminAdvertsPage";
import AdminSettingsPage from "@pages/admin/AdminSettingsPage";
import CompanyOverviewPage from "@pages/company/CompanyOverviewPage";
import CompanyFleetPage from "@pages/company/CompanyFleetPage";
import CompanyRoutesPage from "@pages/company/CompanyRoutesPage";
import CompanyTripsPage from "@pages/company/CompanyTripsPage";
import CompanyBookingsPage from "@pages/company/CompanyBookingsPage";
import CompanyDriversPage from "@pages/company/CompanyDriversPage";
import CompanyReportsPage from "@pages/company/CompanyReportsPage";
import CompanySettingsPage from "@pages/company/CompanySettingsPage";
import { useAuthStore } from "@store/authStore";

function RootRedirect() {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  return (
    <Navigate
      to={user.role === "SUPER_ADMIN" ? "/admin" : "/company"}
      replace
    />
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<LoginPage />} />

      <Route element={<RoleRoute allow="SUPER_ADMIN" />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminOverviewPage />} />
          <Route path="companies" element={<AdminCompaniesPage />} />
          <Route path="bookings" element={<AdminBookingsPage />} />
          <Route path="financials" element={<AdminFinancialsPage />} />
          <Route path="adverts" element={<AdminAdvertsPage />} />
          <Route path="settings" element={<AdminSettingsPage />} />
        </Route>
      </Route>

      <Route element={<RoleRoute allow="COMPANY_STAFF" />}>
        <Route path="/company" element={<CompanyLayout />}>
          <Route index element={<CompanyOverviewPage />} />
          <Route path="fleet" element={<CompanyFleetPage />} />
          <Route path="routes" element={<CompanyRoutesPage />} />
          <Route path="trips" element={<CompanyTripsPage />} />
          <Route path="bookings" element={<CompanyBookingsPage />} />
          <Route path="drivers" element={<CompanyDriversPage />} />
          <Route path="reports" element={<CompanyReportsPage />} />
          <Route path="settings" element={<CompanySettingsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
