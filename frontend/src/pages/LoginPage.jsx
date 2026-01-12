import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LoginForm } from '../features/auth/LoginForm';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const handleSuccess = () => {
    navigate(from, { replace: true });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-center mb-6">Sign In</h2>
      <LoginForm onSuccess={handleSuccess} />
      <p className="mt-6 text-center text-gray-600">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-600 hover:text-primary-500">
          Sign up
        </Link>
      </p>
    </div>
  );
}
