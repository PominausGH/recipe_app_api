import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../hooks/useAuth';
import { Button, Input } from '../../components/ui';

export function LoginForm({ onSuccess }) {
  const { login } = useAuth();
  const [error, setError] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    try {
      setError('');
      await login(data.email, data.password);
      onSuccess?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
          {error}
        </div>
      )}

      <Input
        label="Email"
        type="email"
        {...register('email', { required: 'Email is required' })}
        error={errors.email?.message}
      />

      <Input
        label="Password"
        type="password"
        {...register('password', { required: 'Password is required' })}
        error={errors.password?.message}
      />

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Signing in...' : 'Sign In'}
      </Button>
    </form>
  );
}
