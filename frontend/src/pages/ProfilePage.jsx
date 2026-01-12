import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { authApi } from '../api/auth';
import { Button, Input, Card, Spinner } from '../components/ui';
import { ImageUpload } from '../components/ImageUpload';

export function ProfilePage() {
  const { user, updateProfile, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    try {
      await updateProfile({ name, bio });
      setIsEditing(false);
    } catch (err) {
      setError('Failed to update profile.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePhotoChange = async (file) => {
    if (!file) return;
    try {
      await authApi.updateProfilePhoto(file);
      await refreshUser();
    } catch (err) {
      setError('Failed to upload photo.');
    }
  };

  if (!user) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">My Profile</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <Card className="mb-6">
        <Card.Body className="flex items-center gap-6">
          <div className="relative">
            {user.profile_photo ? (
              <img
                src={user.profile_photo}
                alt={user.name}
                className="w-24 h-24 rounded-full object-cover"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-3xl font-bold">
                {user.name?.[0]?.toUpperCase() || '?'}
              </div>
            )}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold">{user.name}</h2>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-400 mt-1">
              Member since {new Date(user.date_joined).toLocaleDateString()}
            </p>
          </div>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Profile Details</h2>
          {!isEditing && (
            <Button variant="secondary" onClick={() => setIsEditing(true)}>
              Edit
            </Button>
          )}
        </Card.Header>
        <Card.Body>
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bio
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Tell us about yourself..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Profile Photo
                </label>
                <ImageUpload
                  value={user.profile_photo}
                  onChange={handlePhotoChange}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setIsEditing(false);
                    setName(user.name || '');
                    setBio(user.bio || '');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <span className="text-sm text-gray-500">Name</span>
                <p>{user.name || 'Not set'}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Bio</span>
                <p>{user.bio || 'No bio yet'}</p>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
