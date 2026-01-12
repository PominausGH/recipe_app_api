import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useAddComment } from '../hooks/useRecipes';
import { Button, Input } from './ui';

function Comment({ comment, recipeId, onReply }) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyText, setReplyText] = useState('');
  const { isAuthenticated } = useAuth();
  const addComment = useAddComment();

  const handleReply = async (e) => {
    e.preventDefault();
    if (!replyText.trim()) return;
    await addComment.mutateAsync({
      recipeId,
      text: replyText,
      parentId: comment.id,
    });
    setReplyText('');
    setShowReplyForm(false);
  };

  return (
    <div className="border-l-2 border-gray-200 pl-4">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-medium">
          {comment.user?.name?.[0]?.toUpperCase() || '?'}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium">{comment.user?.name || 'Anonymous'}</span>
            <span className="text-gray-400 text-sm">
              {new Date(comment.created_at).toLocaleDateString()}
            </span>
          </div>
          <p className="text-gray-700 mt-1">{comment.text}</p>
          {isAuthenticated && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="text-sm text-primary-600 mt-2 hover:text-primary-700"
            >
              Reply
            </button>
          )}
          {showReplyForm && (
            <form onSubmit={handleReply} className="mt-2 flex gap-2">
              <Input
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Write a reply..."
                className="flex-1"
              />
              <Button type="submit" size="sm" disabled={addComment.isPending}>
                Reply
              </Button>
            </form>
          )}
          {comment.replies?.map((reply) => (
            <div key={reply.id} className="mt-3">
              <Comment comment={reply} recipeId={recipeId} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function CommentThread({ comments, recipeId }) {
  const [newComment, setNewComment] = useState('');
  const { isAuthenticated } = useAuth();
  const addComment = useAddComment();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    await addComment.mutateAsync({ recipeId, text: newComment });
    setNewComment('');
  };

  const topLevelComments = comments?.filter((c) => !c.parent) || [];

  return (
    <div className="space-y-6">
      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
            className="flex-1"
          />
          <Button type="submit" disabled={addComment.isPending}>
            Post
          </Button>
        </form>
      )}

      {topLevelComments.length === 0 ? (
        <p className="text-gray-500 text-center py-4">
          No comments yet. {isAuthenticated ? 'Be the first to comment!' : 'Login to comment.'}
        </p>
      ) : (
        <div className="space-y-4">
          {topLevelComments.map((comment) => (
            <Comment key={comment.id} comment={comment} recipeId={recipeId} />
          ))}
        </div>
      )}
    </div>
  );
}
