import client from "./client";

export const usersApi = {
  async get(id) {
    const response = await client.get(`/interaction/users/${id}/`);
    return response.data;
  },

  async getRecipes(userId, params = {}) {
    const response = await client.get("/recipes/", {
      params: { ...params, author: userId },
    });
    return response.data;
  },

  async follow(userId) {
    const response = await client.post(`/interaction/users/${userId}/follow/`);
    return response.data;
  },

  async getFollowers(userId, page = 1) {
    const response = await client.get(
      `/interaction/users/${userId}/followers/`,
      {
        params: { page },
      },
    );
    return response.data;
  },

  async getFollowing(userId, page = 1) {
    const response = await client.get(
      `/interaction/users/${userId}/following/`,
      {
        params: { page },
      },
    );
    return response.data;
  },
};
