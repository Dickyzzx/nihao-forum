import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './pages/Register';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        {/* 你可以在这里继续添加更多页面 */}
      </Routes>
    </Router>
  );
}
