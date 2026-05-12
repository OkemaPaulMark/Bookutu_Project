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

interface Bus {
  id: string;
  registrationNumber: string;
  model: string;
  year: number;
  capacity: number;
  color: string;
  fuelType: string;
  status: "active" | "maintenance" | "inactive";
  lastMaintenance: string;
  currentMileage: number;
}

export default function CompanyFleetPage() {
  const [showModal, setShowModal] = useState(false);
  const [buses, setBuses] = useState<Bus[]>([
    {
      id: "1",
      registrationNumber: "UBK-001",
      model: "Scania K310",
      year: 2022,
      capacity: 50,
      color: "White",
      fuelType: "Diesel",
      status: "active",
      lastMaintenance: "2025-04-15",
      currentMileage: 45000,
    },
    {
      id: "2",
      registrationNumber: "UBK-002",
      model: "Volvo B9R",
      year: 2021,
      capacity: 45,
      color: "Blue",
      fuelType: "Diesel",
      status: "active",
      lastMaintenance: "2025-05-01",
      currentMileage: 62000,
    },
    {
      id: "3",
      registrationNumber: "UBK-003",
      model: "Mercedes Sprinter",
      year: 2023,
      capacity: 30,
      color: "Silver",
      fuelType: "Diesel",
      status: "maintenance",
      lastMaintenance: "2025-05-10",
      currentMileage: 22000,
    },
    {
      id: "4",
      registrationNumber: "UBK-004",
      model: "Scania K420",
      year: 2020,
      capacity: 50,
      color: "Red",
      fuelType: "Diesel",
      status: "active",
      lastMaintenance: "2025-03-20",
      currentMileage: 78000,
    },
    {
      id: "5",
      registrationNumber: "UBK-005",
      model: "Hyundai County",
      year: 2019,
      capacity: 35,
      color: "White",
      fuelType: "Diesel",
      status: "inactive",
      lastMaintenance: "2024-12-10",
      currentMileage: 95000,
    },
  ]);

  const [formData, setFormData] = useState({
    registrationNumber: "",
    model: "",
    year: new Date().getFullYear(),
    capacity: 50,
    color: "",
    fuelType: "Diesel",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleInputChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "year" || name === "capacity" ? parseInt(value) : value,
    }));
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newBus: Bus = {
        id: Date.now().toString(),
        registrationNumber: formData.registrationNumber,
        model: formData.model,
        year: formData.year,
        capacity: formData.capacity,
        color: formData.color,
        fuelType: formData.fuelType,
        status: "active",
        lastMaintenance: new Date().toISOString().split("T")[0],
        currentMileage: 0,
      };

      setBuses((prev) => [newBus, ...prev]);
      toast.success("Bus added to fleet");

      setFormData({
        registrationNumber: "",
        model: "",
        year: new Date().getFullYear(),
        capacity: 50,
        color: "",
        fuelType: "Diesel",
      });

      setShowModal(false);
      setIsSubmitting(false);
    }, 1000);
  }

  function handleDelete(id: string) {
    if (confirm("Are you sure you want to remove this bus?")) {
      setBuses((prev) => prev.filter((bus) => bus.id !== id));
      toast.success("Bus removed from fleet");
    }
  }

  function handleView(bus: Bus) {
    toast.success(`Viewing ${bus.registrationNumber}`);
  }

  function handleEdit(bus: Bus) {
    setFormData({
      registrationNumber: bus.registrationNumber,
      model: bus.model,
      year: bus.year,
      capacity: bus.capacity,
      color: bus.color,
      fuelType: bus.fuelType,
    });
    setShowModal(true);
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-emerald-100 text-emerald-800";
      case "maintenance":
        return "bg-amber-100 text-amber-800";
      case "inactive":
        return "bg-rose-100 text-rose-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  const activeCount = buses.filter((b) => b.status === "active").length;
  const totalCapacity = buses.reduce((sum, b) => sum + b.capacity, 0);

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Fleet</h1>
          <p className="mt-1 text-sm text-slate-600">
            Manage your company buses and vehicles
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          Add Bus
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-4">
          <p className="text-sm text-slate-600">Total Buses</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {buses.length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Active</p>
          <p className="mt-2 text-2xl font-bold text-emerald-600">
            {activeCount}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-slate-600">Total Capacity</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {totalCapacity} seats
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
                  Reg. Number
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Year
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Capacity
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Fuel Type
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Mileage
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
              {buses.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <AlertCircle size={32} className="text-slate-400" />
                      <p className="text-slate-600">No buses in fleet</p>
                    </div>
                  </td>
                </tr>
              ) : (
                buses.map((bus) => (
                  <tr key={bus.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-3 text-sm font-medium text-blue-600">
                      {bus.registrationNumber}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-900">
                      {bus.model}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {bus.year}
                    </td>
                    <td className="px-6 py-3 text-sm font-medium text-slate-900">
                      {bus.capacity} seats
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {bus.fuelType}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      {bus.currentMileage.toLocaleString()} km
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <span
                        className={`inline-block rounded-full px-3 py-1 text-xs font-semibold capitalize ${getStatusColor(bus.status)}`}
                      >
                        {bus.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleView(bus)}
                          className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded transition"
                          title="View"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => handleEdit(bus)}
                          className="p-1.5 text-slate-600 hover:text-amber-600 hover:bg-amber-50 rounded transition"
                          title="Edit"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(bus.id)}
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
                Add Bus to Fleet
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
                  Registration Number
                </span>
                <input
                  type="text"
                  name="registrationNumber"
                  value={formData.registrationNumber}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  placeholder="UBK-001"
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Bus Model
                </span>
                <input
                  type="text"
                  name="model"
                  value={formData.model}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  placeholder="Scania K310"
                  required
                />
              </label>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">
                    Year
                  </span>
                  <input
                    type="number"
                    name="year"
                    value={formData.year}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                    min="2000"
                    max={new Date().getFullYear()}
                    required
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">
                    Capacity (Seats)
                  </span>
                  <input
                    type="number"
                    name="capacity"
                    value={formData.capacity}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                    min="10"
                    max="100"
                    required
                  />
                </label>
              </div>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Color
                </span>
                <input
                  type="text"
                  name="color"
                  value={formData.color}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                  placeholder="White"
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Fuel Type
                </span>
                <select
                  name="fuelType"
                  value={formData.fuelType}
                  onChange={handleInputChange}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:bg-white"
                >
                  <option>Diesel</option>
                  <option>Petrol</option>
                  <option>Hybrid</option>
                </select>
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
                      Adding...
                    </>
                  ) : (
                    "Add Bus"
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
