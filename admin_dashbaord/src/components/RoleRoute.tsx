import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import type { UserRole } from '@app-types/auth'

type RoleRouteProps = {
  allow: UserRole
}

export default function RoleRoute({ allow }: RoleRouteProps) {
  const user = useAuthStore((state) => state.user)
  const isHydrating = useAuthStore((state) => state.isHydrating)

  if (isHydrating) return null
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== allow) return <Navigate to={user.role === 'SUPER_ADMIN' ? '/admin' : '/company'} replace />

  return <Outlet />
}
