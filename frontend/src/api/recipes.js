import client from "./client";

export const recipesApi = {
  async list(params = {}) {
    const response = await client.get("/recipes/", { params });
    return response.data;
  },

  async get(id) {
    const response = await client.get(`/recipes/${id}/`);
    return response.data;
  },

  async create(data) {
    const response = await client.post("/recipes/", data);
    return response.data;
  },

  async update(id, data) {
    const response = await client.patch(`/recipes/${id}/`, data);
    return response.data;
  },

  async delete(id) {
    await client.delete(`/recipes/${id}/`);
  },

  async uploadImage(id, file) {
    const formData = new FormData();
    formData.append("image", file);
    const response = await client.post(
      `/recipes/${id}/upload-image/`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      },
    );
    return response.data;
  },

  async rate(id, score, review = "") {
    const response = await client.post(`/recipes/${id}/rate/`, {
      score,
      review,
    });
    return response.data;
  },

  async toggleFavorite(id) {
    const response = await client.post(`/recipes/${id}/favorite/`);
    return response.data;
  },

  async getComments(id) {
    const response = await client.get(`/recipes/${id}/comments/`);
    return response.data;
  },

  async addComment(id, text, parentId = null) {
    const data = { text };
    if (parentId) data.parent = parentId;
    const response = await client.post(`/recipes/${id}/comments/`, data);
    return response.data;
  },

  async getMyRecipes(params = {}) {
    const response = await client.get("/recipes/", {
      params: { ...params, author: "me" },
    });
    return response.data;
  },

  async importFromUrl(url) {
    const response = await client.post("/recipes/import-url/", { url });
    return response.data;
  },
};
