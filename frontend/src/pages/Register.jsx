import { useState, useEffect } from 'react';

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

export default function Register() {
  const [method, setMethod] = useState('invite');
  const [nickname, setNickname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [school, setSchool] = useState('');
  const [code, setCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/accounts/csrf/', {
      credentials: 'include',
    });
  }, []);

  const handleSubmit = async () => {
    if (password !== confirmPassword) {
      alert('Passwords do not match!');
      return;
    }

    const formData = {
      nickname,
      email,
      password,
      register_method: method,
      school,
      invite_code: method === 'invite' ? code : '',
      email_code: method === 'email' ? code : '',
    };

    try {
      const response = await fetch('http://localhost:8000/accounts/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (data.success) {
        alert('Registration successful!');
      } else {
        alert(data.message || 'Registration failed.');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
  };

  const sendCode = async () => {
    if (!email.endsWith('.edu')) {
      alert('Please enter a valid .edu email address');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/accounts/send_code/?email=${encodeURIComponent(email)}`, {
        credentials: 'include',
      });

      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error('Invalid response from server');
      }

      if (data.success) {
        alert('Verification code sent! Please check your email.');
      } else {
        alert(data.message || 'Failed to send code.');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white p-6 rounded-2xl shadow-md">
        <h1 className="text-2xl font-bold text-center mb-6">Register</h1>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nickname</label>
            <input
              className="w-full border px-3 py-2 rounded-lg"
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              className="w-full border px-3 py-2 rounded-lg"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

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

          <div>
            <label className="block text-sm font-medium mb-1">Confirm Password</label>
            <div className="relative">
              <input
                className="w-full border px-3 py-2 rounded-lg"
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
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

          <div>
            <label className="block text-sm font-medium mb-1">School</label>
            <select
              className="w-full border px-3 py-2 rounded-lg"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
            >
              <option value="">-- Select School --</option>
              <option value="JHU">JHU</option>
              <option value="CMU">CMU</option>
              <option value="MIT">MIT</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Register Method</label>
            <div className="flex gap-4 mt-1">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  value="invite"
                  checked={method === 'invite'}
                  onChange={() => setMethod('invite')}
                />
                Invite Code
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  value="email"
                  checked={method === 'email'}
                  onChange={() => setMethod('email')}
                />
                Email Code
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Verification Code</label>
            <div className="flex gap-2">
              <input
                className="flex-1 border px-3 py-2 rounded-lg"
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button
                type="button"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg"
                onClick={sendCode}
              >
                Send Code
              </button>
            </div>
          </div>

          <button
            type="button"
            className="w-full py-2 bg-green-500 text-white rounded-lg mt-4"
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}
