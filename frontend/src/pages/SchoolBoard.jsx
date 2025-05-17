import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

export default function SchoolBoard() {
  const { id } = useParams();  // 从 URL 中获取 school_id
  const [schoolName, setSchoolName] = useState('');
  const [posts, setPosts] = useState([]);

  useEffect(() => {
      // 使用环境变量中的后端地址发起请求（上线时只需修改 .env 文件）
    fetch(`${import.meta.env.VITE_BACKEND_URL}/school/${id}/`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
        } else {
          setSchoolName(data.school);
          setPosts(data.posts);
        }
      });
  }, [id]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">{schoolName} Board</h1>
      <div className="space-y-4">
        {posts.map(post => (
          <div key={post.id} className="p-4 bg-white rounded-xl shadow">
            <h2 className="text-lg font-semibold">{post.title}</h2>
            <p className="text-gray-700 mt-2">{post.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
