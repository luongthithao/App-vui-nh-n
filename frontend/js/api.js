import { API_BASE_URL } from "./config.js";

export async function getQuestion(subject, difficulty, excludeIds = []) {
  const params = new URLSearchParams();

  if (excludeIds.length > 0) {
    params.set("exclude_ids", excludeIds.join(","));
  }

  const url = `${API_BASE_URL}/question/${subject}/${difficulty}?${params.toString()}`;

  const response = await fetch(url);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || "Không lấy được câu hỏi từ server";
    throw new Error(message);
  }

  return await response.json();
}