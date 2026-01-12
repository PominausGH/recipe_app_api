import { createContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../../api/auth';
import { setAccessToken, clearTokens } from '../../api/client';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      fetchUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [fetchUser]);

  const login = async (email, password) => {
    await authApi.login(email, password);
    await fetchUser();
  };

  const register = async (email, name, password, passwordConfirm) => {
    await authApi.register(email, name, password, passwordConfirm);
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  const updateProfile = async (data) => {
    const updatedUser = await authApi.updateMe(data);
    setUser(updatedUser);
    return updatedUser;
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
    refreshUser: fetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
