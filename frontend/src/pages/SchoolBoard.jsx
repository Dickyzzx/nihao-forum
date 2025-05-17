import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';  // ✅ 加入 Link 用于点击跳转

export default function SchoolBoard() {
  const { slug } = useParams(); // ✅ 使用 slug 获取当前学校
  const [schoolName, setSchoolName] = useState('');
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  // -----------------------------
  // 获取 CSRF Token（用于 POST 请求）
  // -----------------------------
  const getCookie = (name) => {
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
  };

  // -----------------------------
  // 加载学校信息与帖子列表
  // -----------------------------
  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/school/${slug}/`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
        } else {
          setSchoolName(data.school);
          setPosts(data.posts);
        }
      });
  }, [slug]);

  // -----------------------------
  // 处理发帖请求
  // -----------------------------
  const handlePost = async () => {
    if (!title || !content) {
      alert('Please fill in both title and content.');
      return;
    }

    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/school/${slug}/post/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'include',
        body: JSON.stringify({ title, content }),
      });

      const data = await res.json();
      if (data.success) {
        setTitle('');
        setContent('');
        setPosts(prev => [data.post, ...prev]); // ✅ 新帖置顶
      } else {
        alert(data.message || 'Failed to post.');
      }
    } catch (err) {
      alert('Network error.');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">{schoolName} Board</h1>

      {/* 发帖区域 */}
      <div className="mb-6 bg-white p-4 rounded-xl shadow space-y-4">
        <h2 className="text-lg font-semibold">Create a Post</h2>
        <input
          className="w-full border px-3 py-2 rounded-lg"
          type="text"
          placeholder="Post Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          className="w-full border px-3 py-2 rounded-lg"
          rows="4"
          placeholder="Write your content here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button
          onClick={handlePost}
          className="px-4 py-2 bg-green-600 text-white rounded-lg"
        >
          Publish
        </button>
      </div>

      {/* 帖子展示区域 */}
      <div className="space-y-4">
        {posts.map(post => (
          <div key={post.id} className="p-4 bg-white rounded-xl shadow">
            {/* ✅ 可点击跳转到帖子详情页 */}
            <Link to={`/post/${post.id}/`}>
              <h2 className="text-lg font-semibold text-blue-600 hover:underline">
                {post.title}
              </h2>
            </Link>
            <p className="text-gray-700 mt-2">{post.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
