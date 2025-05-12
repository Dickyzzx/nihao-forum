import { useState } from 'react'

export default function Register() {
  const [formData, setFormData] = useState({
    first_name: '',
    username: '',
    password: '',
  })

  const [message, setMessage] = useState(null)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const res = await fetch('http://127.0.0.1:8000/accounts/api/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    const data = await res.json()
    setMessage(res.ok ? '✅ 注册成功，请前往登录' : '❌ 注册失败，请检查填写内容')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md bg-white p-6 rounded-xl shadow-md">
        <form onSubmit={handleSubmit} className="w-full flex flex-col space-y-6">
          <h2 className="text-2xl font-bold text-center text-gray-800">注册 nihao.com</h2>
          {message && <p className="text-center text-sm text-blue-600">{message}</p>}

          {/* 昵称 */}
          <div className="space-y-1">
            <div className="text-sm text-gray-700">用户名（昵称）</div>
            <div>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="请输入昵称"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                required
              />
            </div>
          </div>

          {/* 账号 */}
          <div className="space-y-1">
            <div className="text-sm text-gray-700">账号</div>
            <div>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="请输入账号"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                required
              />
            </div>
          </div>

          {/* 密码 */}
          <div className="space-y-1">
            <div className="text-sm text-gray-700">密码</div>
            <div>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="请输入密码"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition text-sm font-semibold"
          >
            注册
          </button>
        </form>
      </div>
    </div>
  )
}
