import client from "./client";

export const usersApi = {
  async get(id) {
    const response = await client.get(`/users/${id}/`);
    return response.data;
  },

  async getRecipes(userId, params = {}) {
    const response = await client.get("/recipes/", {
      params: { ...params, author: userId },
    });
    return response.data;
  },

  async follow(userId) {
    const response = await client.post(`/users/${userId}/follow/`);
    return response.data;
  },

  async getFollowers(userId, page = 1) {
    const response = await client.get(`/users/${userId}/followers/`, {
      params: { page },
    });
    return response.data;
  },

  async getFollowing(userId, page = 1) {
    const response = await client.get(`/users/${userId}/following/`, {
      params: { page },
    });
    return response.data;
  },
};
