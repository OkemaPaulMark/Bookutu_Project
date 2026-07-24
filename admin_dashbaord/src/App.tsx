import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import RoleRoute from "@components/RoleRoute";
import CompanyLayout from "@layouts/CompanyLayout";
import LoginPage from "@pages/auth/LoginPage";
import SetPasswordPage from "@pages/auth/SetPasswordPage";
import CompanyOverviewPage from "@pages/company/CompanyOverviewPage";
import CompanyFleetPage from "@pages/company/CompanyFleetPage";
import CompanyRoutesPage from "@pages/company/CompanyRoutesPage";
import CompanyTripsPage from "@pages/company/CompanyTripsPage";
import CompanyBookingsPage from "@pages/company/CompanyBookingsPage";
import CompanyDriversPage from "@pages/company/CompanyDriversPage";
import CompanyDeliveriesPage from "@pages/company/CompanyDeliveriesPage";
import CompanyPassengersPage from "@pages/company/CompanyPassengersPage";
import CompanyAdvertsPage from "@pages/company/CompanyAdvertsPage";
import CompanyFinancialsPage from "@pages/company/CompanyFinancialsPage";
import CompanyStaffPage from "@pages/company/CompanyStaffPage";
import CompanySettingsPage from "@pages/company/CompanySettingsPage";
import { useAuthStore } from "@store/authStore";

function RootRedirect() {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to="/company" replace />;
}

export default function App() {
  const restoreSession = useAuthStore((s) => s.restoreSession);

  useEffect(() => {
    void restoreSession();
  }, [restoreSession]);

  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/set-password" element={<SetPasswordPage />} />

      <Route element={<RoleRoute allow="COMPANY_STAFF" />}>
        <Route path="/company" element={<CompanyLayout />}>
          <Route index element={<CompanyOverviewPage />} />
          <Route path="fleet" element={<CompanyFleetPage />} />
          <Route path="routes" element={<CompanyRoutesPage />} />
          <Route path="trips" element={<CompanyTripsPage />} />
          <Route path="bookings" element={<CompanyBookingsPage />} />
          <Route path="drivers" element={<CompanyDriversPage />} />
          <Route path="deliveries" element={<CompanyDeliveriesPage />} />
          <Route path="passengers" element={<CompanyPassengersPage />} />
          <Route path="adverts" element={<CompanyAdvertsPage />} />
          <Route path="financials" element={<CompanyFinancialsPage />} />
          <Route path="staff" element={<CompanyStaffPage />} />
          <Route path="settings" element={<CompanySettingsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
