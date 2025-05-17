import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import SchoolBoard from './pages/SchoolBoard';
import PostDetail from './pages/PostDetail';  

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/school/:slug" element={<SchoolBoard />} /> 
        <Route path="/post/:postId/" element={<PostDetail />} />
      </Routes>
    </Router>
  );
}
