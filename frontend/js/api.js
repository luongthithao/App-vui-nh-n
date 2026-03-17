import { API_BASE_URL } from "./config.js";

export async function getQuestion(subject, difficulty, excludeIds = []) {
  const cleanedIds = Array.isArray(excludeIds)
    ? excludeIds
        .filter((id) => Number.isInteger(id) || /^\d+$/.test(String(id)))
        .map((id) => Number(id))
    : [];

  const exclude = cleanedIds.join(",");

  const url =
    `${API_BASE_URL}/question/${subject}/${difficulty}` +
    `?exclude_ids=${encodeURIComponent(exclude)}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  });

  if (!response.ok) {
    let message = "Không tải được câu hỏi";

    try {
      const errorData = await response.json();
      if (errorData?.detail) {
        message = errorData.detail;
      }
    } catch (_) {}

    throw new Error(message);
  }

  return response.json();
}