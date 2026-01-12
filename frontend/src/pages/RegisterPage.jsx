import { Link, useNavigate } from 'react-router-dom';
import { RegisterForm } from '../features/auth/RegisterForm';

export function RegisterPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    navigate('/login', { state: { message: 'Account created! Please sign in.' } });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-center mb-6">Create Account</h2>
      <RegisterForm onSuccess={handleSuccess} />
      <p className="mt-6 text-center text-gray-600">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-600 hover:text-primary-500">
          Sign in
        </Link>
      </p>
    </div>
  );
}
