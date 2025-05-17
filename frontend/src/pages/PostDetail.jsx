import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

export default function PostDetail() {
  const { postId } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  // 获取 CSRF Token
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

  // 加载帖子详情 + 评论
  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/school/post/${postId}/`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
        } else {
          setPost(data);
          setComments(data.comments);
        }
      });
  }, [postId]);

  // 发表评论（顶层）
  const handleComment = async () => {
    if (!newComment.trim()) return;
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/school/post/${postId}/comment/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'include',
        body: JSON.stringify({ content: newComment }),
      });
      const data = await res.json();
      if (data.success) {
        setComments(prev => [...prev, { ...data.comment, replies: [] }]);
        setNewComment('');
      }
    } catch {
      alert('Network error.');
    }
  };

  if (!post) return <div className="p-4">Loading...</div>;

  // ✅ 每条评论自己管理 replyVisible 和 replyContent
  const CommentItem = ({ comment, depth = 0 }) => {
    const [replyVisible, setReplyVisible] = useState(false);
    const [replyContent, setReplyContent] = useState('');

    const handleReply = async () => {
      if (!replyContent.trim()) return;
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/school/post/${postId}/comment/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          credentials: 'include',
          body: JSON.stringify({ content: replyContent, parent_id: comment.id }),
        });
        const data = await res.json();
        if (data.success) {
          const addReply = (list) =>
            list.map(c =>
              c.id === comment.id
                ? { ...c, replies: [...c.replies, { ...data.comment, replies: [] }] }
                : { ...c, replies: addReply(c.replies) }
            );
          setComments(prev => addReply(prev));
          setReplyContent('');
          setReplyVisible(false);
        }
      } catch {
        alert('Network error.');
      }
    };

    return (
      <div className={`pt-4 ${depth > 0 ? 'pl-4 border-l' : ''}`}>
        <p className="text-sm text-gray-600">{comment.author} · {comment.created_at}</p>
        <p className="text-gray-800 mt-1">{comment.content}</p>
        <button
          onClick={() => setReplyVisible(!replyVisible)}
          className="text-blue-600 text-sm mt-2"
        >
          {replyVisible ? 'Cancel' : 'Reply'}
        </button>

        {replyVisible && (
          <div className="mt-2">
            <textarea
              className="w-full border px-3 py-2 rounded-lg mt-2"
              rows="2"
              placeholder="Write a reply..."
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
            />
            <button
              onClick={handleReply}
              className="mt-1 px-3 py-1 bg-blue-500 text-white rounded-lg text-sm"
            >
              Post Reply
            </button>
          </div>
        )}

        {comment.replies && comment.replies.length > 0 && (
          <div className="mt-4 space-y-4">
            {comment.replies.map(reply => (
              <CommentItem key={reply.id} comment={reply} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <div className="bg-white p-6 rounded-xl shadow mb-6">
        <h1 className="text-2xl font-bold mb-2">{post.title}</h1>
        <p className="text-gray-600 text-sm mb-4">
          By {post.author} · {post.created_at}
        </p>
        <p className="text-gray-800">{post.content}</p>
      </div>

      <div className="bg-white p-6 rounded-xl shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Comments</h2>

        {comments.length === 0 ? (
          <p className="text-gray-500">No comments yet.</p>
        ) : (
          comments.map(comment => (
            <CommentItem key={comment.id} comment={comment} />
          ))
        )}

        <div className="mt-6">
          <textarea
            className="w-full border px-3 py-2 rounded-lg"
            rows="3"
            placeholder="Write a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
          />
          <button
            onClick={handleComment}
            className="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg"
          >
            Post Comment
          </button>
        </div>
      </div>
    </div>
  );
}
