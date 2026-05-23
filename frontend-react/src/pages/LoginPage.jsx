import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginApi } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const [employeeId, setEmployeeId] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  function validate() {
    const errs = {}
    if (!employeeId.trim()) errs.employeeId = '社員IDを入力してください'
    if (!password) {
      errs.password = 'パスワードを入力してください'
    } else if (password.length < 8) {
      errs.password = 'パスワードは8文字以上で入力してください'
    } else if (!/^[\x20-\x7E]+$/.test(password)) {
      errs.password = 'パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）'
    }
    return errs
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    const errs = validate()
    setFieldErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    try {
      const data = await loginApi({ employee_id: employeeId, password })
      const payloadPart = data.access_token.split('.')[1]
      const decoded = JSON.parse(atob(payloadPart))
      login(data.access_token, {
        employee_id: decoded.sub,
        name: decoded.name,
        role: decoded.role,
      })
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail ?? 'ログインに失敗しました。もう一度お試しください。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-logo">Attend<span>Ease</span></div>

      <div className="auth-card">
        <h1 className="auth-title">社員ログイン</h1>

        {error && <div className="auth-alert">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="auth-field">
              <label className="auth-label">
                社員ID<span className="required-mark">※</span>
              </label>
              <input
                className={`auth-input${fieldErrors.employeeId ? ' has-error' : ''}`}
                type="text"
                value={employeeId}
                onChange={e => setEmployeeId(e.target.value)}
                placeholder="例: EMP001"
                autoComplete="username"
                disabled={loading}
              />
              {fieldErrors.employeeId && (
                <span className="field-error">{fieldErrors.employeeId}</span>
              )}
            </div>

            <div className="auth-field">
              <label className="auth-label">
                パスワード<span className="required-mark">※</span>
              </label>
              <div className="auth-input-wrap">
                <input
                  className={`auth-input${fieldErrors.password ? ' has-error' : ''}`}
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="パスワードを入力"
                  autoComplete="current-password"
                  disabled={loading}
                  style={{ paddingRight: '52px' }}
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowPassword(v => !v)}
                  tabIndex={-1}
                  aria-label={showPassword ? 'パスワードを隠す' : 'パスワードを表示'}
                >
                  {showPassword ? '隠す' : '表示'}
                </button>
              </div>
              <span className="auth-hint">半角英数字・記号のみ（8文字以上）</span>
              {fieldErrors.password && (
                <span className="field-error">{fieldErrors.password}</span>
              )}
            </div>

            <button className="auth-btn" type="submit" disabled={loading}>
              {loading ? 'ログイン中...' : 'ログイン'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
