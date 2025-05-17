import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import SchoolBoard from './pages/SchoolBoard';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/school/:id" element={<SchoolBoard />} />  {/* ✅ 新增 */}
        {/* 你可以在这里继续添加更多页面 */}
      </Routes>
    </Router>
  );
}
