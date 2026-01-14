import client, { setAccessToken, clearTokens } from "./client";

export const authApi = {
  async login(email, password) {
    const response = await client.post("/auth/login/", { email, password });
    const { access, refresh } = response.data;
    setAccessToken(access);
    localStorage.setItem("refreshToken", refresh);
    return response.data;
  },

  async register(email, name, password, password_confirm) {
    const response = await client.post("/auth/register/", {
      email,
      name,
      password,
      password_confirm,
    });
    return response.data;
  },

  async logout() {
    const refreshToken = localStorage.getItem("refreshToken");
    if (refreshToken) {
      try {
        await client.post("/auth/logout/", { refresh: refreshToken });
      } catch {
        // Ignore logout errors
      }
    }
    clearTokens();
  },

  async getMe() {
    const response = await client.get("/auth/me/");
    return response.data;
  },

  async updateMe(data) {
    const response = await client.patch("/auth/me/", data);
    return response.data;
  },

  async updateProfilePhoto(file) {
    const formData = new FormData();
    formData.append("profile_photo", file);
    const response = await client.patch("/auth/me/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },
};
