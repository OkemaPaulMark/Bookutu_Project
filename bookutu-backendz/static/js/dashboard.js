/**
 * Dashboard JavaScript functionality for Bookutu
 * Handles charts, real-time updates, and interactive elements
 */
class DashboardManager {
  constructor() {
    this.charts = {}
    this.init()
  }

  init() {
    this.initializeCharts()
    this.setupEventListeners()
    this.startRealTimeUpdates()
  }

  initializeCharts() {
    // Initialize booking trends chart
    if (document.getElementById("bookingsChart")) {
      this.initBookingsChart()
    }

    // Initialize revenue chart
    if (document.getElementById("revenueChart")) {
      this.initRevenueChart()
    }
  }

  initBookingsChart() {
    const ctx = document.getElementById("bookingsChart").getContext("2d")

    // Get data from template context or default values
    const bookingData = window.weeklyBookingsData || [120, 145, 132, 158, 147, 210, 194]

    this.charts.bookings = new Chart(ctx, {
      type: "line",
      data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [
          {
            label: "Bookings",
            data: bookingData,
            borderColor: "#0ea5e9",
            backgroundColor: "rgba(14, 165, 233, 0.1)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false,
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    })
  }

  initRevenueChart() {
    const ctx = document.getElementById("revenueChart").getContext("2d")

    // Check if this is company or admin dashboard
    const isAdminDashboard = document.body.classList.contains("admin-dashboard")

    if (isAdminDashboard) {
      // Doughnut chart for admin dashboard
      const revenueDistribution = window.revenueDistributionData || [35, 28, 15, 22]

      this.charts.revenue = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["Jaguar Coaches", "Gateway Bus", "Mega Bus", "Others"],
          datasets: [
            {
              data: revenueDistribution,
              backgroundColor: [
                "rgba(14, 165, 233, 0.8)",
                "rgba(217, 70, 239, 0.8)",
                "rgba(20, 184, 166, 0.8)",
                "rgba(156, 163, 175, 0.8)",
              ],
              borderWidth: 0,
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "right",
            },
          },
          cutout: "70%",
        },
      })
    } else {
      // Bar chart for company dashboard
      const routeRevenueData = window.routeRevenueData || [1200000, 950000, 650000, 880000, 720000]

      this.charts.revenue = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Kampala-Gulu", "Kampala-Mbarara", "Kampala-Jinja", "Kampala-Lira", "Kampala-Fort Portal"],
          datasets: [
            {
              label: "Revenue (UGX)",
              data: routeRevenueData,
              backgroundColor: [
                "rgba(14, 165, 233, 0.8)",
                "rgba(217, 70, 239, 0.8)",
                "rgba(20, 184, 166, 0.8)",
                "rgba(245, 158, 11, 0.8)",
                "rgba(139, 92, 246, 0.8)",
              ],
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                drawBorder: false,
              },
              ticks: {
                callback: (value) => "UGX " + (value / 1000000).toFixed(1) + "M",
              },
            },
            x: {
              grid: {
                display: false,
              },
            },
          },
        },
      })
    }
  }

  setupEventListeners() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector(".mobile-menu-btn")
    if (mobileMenuBtn) {
      mobileMenuBtn.addEventListener("click", this.toggleMobileMenu.bind(this))
    }

    // Notification dropdown
    const notificationBtn = document.querySelector(".notification-btn")
    if (notificationBtn) {
      notificationBtn.addEventListener("click", this.toggleNotifications.bind(this))
    }

    // Search functionality
    const searchInput = document.querySelector(".search-input")
    if (searchInput) {
      searchInput.addEventListener("input", this.handleSearch.bind(this))
    }

    // Chart period selectors
    document.querySelectorAll(".chart-period-selector").forEach((selector) => {
      selector.addEventListener("change", this.updateChartPeriod.bind(this))
    })
  }

  toggleMobileMenu() {
    const sidebar = document.querySelector(".sidebar")
    const mainContent = document.querySelector(".main-content")

    sidebar.classList.toggle("mobile-hidden")
    mainContent.classList.toggle("mobile-expanded")
  }

  toggleNotifications() {
    const dropdown = document.querySelector(".notification-dropdown")
    if (dropdown) {
      dropdown.classList.toggle("hidden")
    }
  }

  handleSearch(event) {
    const query = event.target.value.toLowerCase()
    // Implement search functionality based on current page
    console.log("Searching for:", query)
  }

  updateChartPeriod(event) {
    const period = event.target.value
    const chartType = event.target.dataset.chart

    // Show loading state
    this.showChartLoading(chartType)

    // Fetch new data based on period
    this.fetchChartData(chartType, period)
      .then((data) => this.updateChart(chartType, data))
      .catch((error) => console.error("Error updating chart:", error))
      .finally(() => this.hideChartLoading(chartType))
  }

  showChartLoading(chartType) {
    const container = document.querySelector(`#${chartType}Chart`).closest(".chart-container")
    container.classList.add("loading")
  }

  hideChartLoading(chartType) {
    const container = document.querySelector(`#${chartType}Chart`).closest(".chart-container")
    container.classList.remove("loading")
  }

  async fetchChartData(chartType, period) {
    const response = await fetch(`/api/dashboard/${chartType}-data/?period=${period}`, {
      headers: {
        "X-CSRFToken": this.getCSRFToken(),
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch chart data")
    }

    return response.json()
  }

  updateChart(chartType, data) {
    const chart = this.charts[chartType]
    if (chart) {
      chart.data.datasets[0].data = data.values
      if (data.labels) {
        chart.data.labels = data.labels
      }
      chart.update()
    }
  }

  startRealTimeUpdates() {
    // Update dashboard stats every 30 seconds
    setInterval(() => {
      this.updateDashboardStats()
    }, 30000)
  }

  async updateDashboardStats() {
    try {
      const response = await fetch("/api/dashboard/live-stats/", {
        headers: {
          "X-CSRFToken": this.getCSRFToken(),
        },
      })

      if (response.ok) {
        const stats = await response.json()
        this.updateStatCards(stats)
      }
    } catch (error) {
      console.error("Error updating dashboard stats:", error)
    }
  }

  updateStatCards(stats) {
    // Update stat cards with new data
    Object.keys(stats).forEach((key) => {
      const element = document.querySelector(`[data-stat="${key}"]`)
      if (element) {
        element.textContent = this.formatStatValue(key, stats[key])
      }
    })
  }

  formatStatValue(key, value) {
    if (key.includes("revenue")) {
      return `UGX ${(value / 1000000).toFixed(1)}M`
    } else if (key.includes("rate") || key.includes("percentage")) {
      return `${value}%`
    }
    return value.toLocaleString()
  }

  getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || ""
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new DashboardManager()
})

// Utility functions
function showToast(message, type = "info") {
  const toast = document.createElement("div")
  toast.className = `toast toast-${type}`
  toast.textContent = message

  document.body.appendChild(toast)

  setTimeout(() => {
    toast.classList.add("show")
  }, 100)

  setTimeout(() => {
    toast.classList.remove("show")
    setTimeout(() => document.body.removeChild(toast), 300)
  }, 3000)
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-UG", {
    style: "currency",
    currency: "UGX",
    minimumFractionDigits: 0,
  }).format(amount)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("en-UG", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}
