import { useState, useEffect } from 'react';

// -----------------------------
// 获取 CSRF Token 的工具函数
// -----------------------------
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default function Login() {
  // -----------------------------
  // 表单状态变量
  // -----------------------------
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // -----------------------------
  // 初次加载时，向后端请求 CSRF Token（仅获取，不使用）
  // -----------------------------
  useEffect(() => {
    fetch('http://localhost:8000/accounts/csrf/', {
      credentials: 'include',
    });
  }, []);

  // -----------------------------
  // 登录提交处理函数
  // -----------------------------
  const handleLogin = async () => {
    if (!email || !password) {
      alert('Please enter both email and password.');
      return;
    }

    const payload = {
      email,
      password,
    };

    try {
      const response = await fetch('http://localhost:8000/accounts/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),  // 设置 CSRF Token
        },
        credentials: 'include',  // 包含 Cookie（用于认证）
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      // ✅ 登录成功，跳转到该用户所属学校的板块页面（用 slug）
      if (data.success && data.school_slug) {
        window.location.href = `/school/${data.school_slug}/`;
      } else {
        alert(data.message || 'Login failed.');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
  };

  // -----------------------------
  // 登录表单界面
  // -----------------------------
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white p-6 rounded-2xl shadow-md">
        <h1 className="text-2xl font-bold text-center mb-6">Login</h1>

        <div className="space-y-4">
          {/* 邮箱输入框 */}
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              className="w-full border px-3 py-2 rounded-lg"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* 密码输入框（可显示/隐藏） */}
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <div className="relative">
              <input
                className="w-full border px-3 py-2 rounded-lg"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-blue-500"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {/* 登录按钮 */}
          <button
            type="button"
            className="w-full py-2 bg-green-500 text-white rounded-lg mt-4"
            onClick={handleLogin}
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
}
