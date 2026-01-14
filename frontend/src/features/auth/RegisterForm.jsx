import { useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../../hooks/useAuth";
import { Button, Input } from "../../components/ui";

export function RegisterForm({ onSuccess }) {
  const { register: registerUser } = useAuth();
  const [error, setError] = useState("");
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm();
  const password = watch("password");

  const onSubmit = async (data) => {
    try {
      setError("");
      await registerUser(
        data.email,
        data.name,
        data.password,
        data.password_confirm,
      );
      onSuccess?.();
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData) {
        const messages = Object.values(errorData).flat().join(" ");
        setError(messages || "Registration failed.");
      } else {
        setError("Registration failed. Please try again.");
      }
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
        label="Name"
        {...register("name", { required: "Name is required" })}
        error={errors.name?.message}
      />

      <Input
        label="Email"
        type="email"
        {...register("email", { required: "Email is required" })}
        error={errors.email?.message}
      />

      <Input
        label="Password"
        type="password"
        {...register("password", {
          required: "Password is required",
          minLength: {
            value: 8,
            message: "Password must be at least 8 characters",
          },
        })}
        error={errors.password?.message}
      />

      <Input
        label="Confirm Password"
        type="password"
        {...register("password_confirm", {
          required: "Please confirm your password",
          validate: (value) => value === password || "Passwords do not match",
        })}
        error={errors.password_confirm?.message}
      />

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Creating account..." : "Create Account"}
      </Button>
    </form>
  );
}
