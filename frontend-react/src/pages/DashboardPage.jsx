import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function DashboardPage() {
  const { auth, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="dashboard">
      <h1>ダッシュボード</h1>
      <p>ようこそ、{auth?.user?.name ?? auth?.user?.employee_id} さん</p>
      <p style={{ fontSize: '0.85rem', color: '#9ca3af' }}>ロール: {auth?.user?.role}</p>
      <button className="dashboard-logout" onClick={handleLogout}>
        ログアウト
      </button>
    </div>
  )
}
