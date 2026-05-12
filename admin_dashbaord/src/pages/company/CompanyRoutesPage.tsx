import { FormEvent, useState } from "react";
import {
  Eye,
  Edit2,
  Trash2,
  Plus,
  X,
  Loader2,
  AlertCircle,
} from "lucide-react";
import toast from "react-hot-toast";

interface Route {
  id: string;
  name: string;
  from: string;
  to: string;
  distance: number;
  fare: number;
  estimatedTime: string;
  operatingDays: string;
  stops: number;
  status: "active" | "inactive" | "suspended";
  createdDate: string;
}

export default function CompanyRoutesPage() {
  const [showModal, setShowModal] = useState(false);
  const [routes, setRoutes] = useState<Route[]>([
    {
      id: "1",
      name: "Kampala - Masaka",
      from: "Kampala",
      to: "Masaka",
      distance: 135,
      fare: 25000,
      estimatedTime: "3 hours",
      operatingDays: "Daily",
      stops: 3,
      status: "active",
      createdDate: "2025-01-10",
    },
    {
      id: "2",
      name: "Kampala - Jinja",
      from: "Kampala",
      to: "Jinja",
      distance: 81,
      fare: 18000,
      estimatedTime: "2 hours",
      operatingDays: "Daily",
      stops: 2,
      status: "active",
      createdDate: "2025-01-15",
    },
    {
      id: "3",
      name: "Kampala - Fort Portal",
      from: "Kampala",
      to: "Fort Portal",
      distance: 280,
      fare: 45000,
      estimatedTime: "5 hours",
      operatingDays: "Mon, Wed, Fri, Sat, Sun",
      stops: 5,
      status: "active",
      createdDate: "2025-02-01",
    },
    {
      id: "4",
      name: "Masaka - Mbarara",
      from: "Masaka",
      to: "Mbarara",
      distance: 120,
      fare: 35000,
      estimatedTime: "3.5 hours",
      operatingDays: "Daily",
      stops: 2,
      status: "inactive",
      createdDate: "2025-01-20",
    },
    {
      id: "5",
      name: "Jinja - Soroti",
      from: "Jinja",
      to: "Soroti",
      distance: 180,
      fare: 40000,
      estimatedTime: "4 hours",
      operatingDays: "Tue, Thu, Sat",
      stops: 4,
      status: "active",
      createdDate: "2025-02-10",
    },
  ]);

  const [formData, setFormData] = useState({
    name: "",
    from: "",
    to: "",
    distance: 0,
    fare: 0,
    estimatedTime: "",
    operatingDays: "Daily",
    stops: 1,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleInputChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "distance" || name === "fare" || name === "stops"
          ? parseInt(value)
          : value,
    }));
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newRoute: Route = {
        id: Date.now().toString(),
        name: formData.name,
        from: formData.from,
        to: formData.to,
        distance: formData.distance,
        fare: formData.fare,
        estimatedTime: formData.estimatedTime,
        operatingDays: formData.operatingDays,
        stops: formData.stops,
        status: "active",
        createdDate: new Date().toISOString().split("T")[0],
      };

      setRoutes((prev) => [newRoute, ...prev]);
      toast.success("Route created successfully");

      setFormData({
        name: "",
        from: "",
        to: "",
        distance: 0,
        fare: 0,
        estimatedTime: "",
        operatingDays: "Daily",
        stops: 1,
      });

      setShowModal(false);
      setIsSubmitting(false);
    }, 1000);
  }

  function handleDelete(id: string) {
    if (confirm("Are you sure you want to delete this route?")) {
      setRoutes((prev) => prev.filter((route) => route.id !== id));
      toast.success("Route deleted");
    }
  }

  function handleView(route: Route) {
    toast.success(`Viewing ${route.name}`);
  }

  function handleEdit(route: Route) {
    setFormData({
      name: route.name,
      from: route.from,
      to: route.to,
      distance: route.distance,
      fare: route.fare,
      estimatedTime: route.estimatedTime,
      operatingDays: route.operatingDays,
      stops: route.stops,
    });
    setShowModal(true);
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-emerald-100 text-emerald-800";
      case "inactive":
        return "bg-slate-100 text-slate-800";
      case "suspended":
        return "bg-rose-100 text-rose-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  const activeRoutes = routes.filter((r) => r.status === "active").length;

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">
            Routes & Schedules
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Define and manage transport routes
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          Create Route
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-4">
          <p className="text-sm text-slate-600">Total Routes</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {routes.length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Active Routes</p>
          <p className="mt-2 text-2xl font-bold text-emerald-600">
            {activeRoutes}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Average Fare</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            UGX{" "}
            {Math.round(
              routes.reduce((sum, r) => sum + r.fare, 0) / routes.length,
            ).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Route Name
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  From
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  To
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Distance
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Fare
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Stops
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {routes.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <AlertCircle size={32} className="text-slate-400" />
                      <p className="text-slate-600">No routes created yet</p>
                    </div>
                  </td>
                </tr>
              ) : (
                routes.map((route) => (
                  <tr key={route.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-3 text-sm font-medium text-blue-600">
                      {route.name}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-900">
                      {route.from}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-900">
                      {route.to}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {route.distance} km
                    </td>
                    <td className="px-6 py-3 text-sm font-semibold text-slate-900">
                      UGX {route.fare.toLocaleString()}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {route.estimatedTime}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {route.stops}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <span
                        className={`inline-block rounded-full px-3 py-1 text-xs font-semibold capitalize ${getStatusColor(route.status)}`}
                      >
                        {route.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleView(route)}
                          className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded transition"
                          title="View"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => handleEdit(route)}
                          className="p-1.5 text-slate-600 hover:text-amber-600 hover:bg-amber-50 rounded transition"
                          title="Edit"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(route.id)}
                          className="p-1.5 text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded transition"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card max-h-[90vh] w-full max-w-md overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900">
                Create Route
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-500 hover:text-slate-700 transition"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <form onSubmit={handleSubmit} className="space-y-5 p-6">
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Route Name
                </span>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  placeholder="Kampala - Masaka"
                  required
                />
              </label>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">
                    From
                  </span>
                  <input
                    type="text"
                    name="from"
                    value={formData.from}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                    placeholder="Kampala"
                    required
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">
                    To
                  </span>
                  <input
                    type="text"
                    name="to"
                    value={formData.to}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                    placeholder="Masaka"
                    required
                  />
                </label>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">
                    Distance (km)
                  </span>
                  <input
                    type="number"
                    name="distance"
                    value={formData.distance}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                    min="1"
                    required
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">
                    Fare (UGX)
                  </span>
                  <input
                    type="number"
                    name="fare"
                    value={formData.fare}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                    min="1000"
                    step="1000"
                    required
                  />
                </label>
              </div>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Estimated Time
                </span>
                <input
                  type="text"
                  name="estimatedTime"
                  value={formData.estimatedTime}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  placeholder="3 hours"
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Operating Days
                </span>
                <input
                  type="text"
                  name="operatingDays"
                  value={formData.operatingDays}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  placeholder="Daily"
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Number of Stops
                </span>
                <input
                  type="number"
                  name="stops"
                  value={formData.stops}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  min="1"
                  required
                />
              </label>

              {/* Modal Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 rounded-lg border border-slate-200 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Route"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
