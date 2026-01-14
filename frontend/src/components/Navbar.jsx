import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { Button } from "./ui";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-primary-600">
              RecipeApp
            </Link>
            <div className="hidden md:flex ml-10 space-x-4">
              <Link
                to="/recipes"
                className="text-gray-700 hover:text-primary-600 px-3 py-2"
              >
                Browse Recipes
              </Link>
              {isAuthenticated && (
                <>
                  <Link
                    to="/recipes/new"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2"
                  >
                    Create Recipe
                  </Link>
                  <Link
                    to="/my-recipes"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2"
                  >
                    My Recipes
                  </Link>
                  <Link
                    to="/favorites"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2"
                  >
                    Favorites
                  </Link>
                </>
              )}
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="text-gray-700 hover:text-primary-600"
                >
                  {user?.name || "Profile"}
                </Link>
                <Button variant="ghost" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost">Login</Button>
                </Link>
                <Link to="/register">
                  <Button>Sign Up</Button>
                </Link>
              </>
            )}
          </div>

          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t">
          <div className="px-4 py-2 space-y-1">
            <Link to="/recipes" className="block px-3 py-2 text-gray-700">
              Browse Recipes
            </Link>
            {isAuthenticated ? (
              <>
                <Link
                  to="/recipes/new"
                  className="block px-3 py-2 text-gray-700"
                >
                  Create Recipe
                </Link>
                <Link
                  to="/my-recipes"
                  className="block px-3 py-2 text-gray-700"
                >
                  My Recipes
                </Link>
                <Link to="/favorites" className="block px-3 py-2 text-gray-700">
                  Favorites
                </Link>
                <Link to="/profile" className="block px-3 py-2 text-gray-700">
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="block px-3 py-2 text-gray-700"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="block px-3 py-2 text-gray-700">
                  Login
                </Link>
                <Link to="/register" className="block px-3 py-2 text-gray-700">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
