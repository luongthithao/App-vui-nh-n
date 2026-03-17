import { API_BASE_URL } from "./config.js";

export async function getQuestion(subject, difficulty, excludeIds = []) {
  const cleanedIds = Array.isArray(excludeIds)
    ? excludeIds
        .filter((id) => Number.isInteger(id) || /^\d+$/.test(String(id)))
        .map((id) => Number(id))
    : [];

  const exclude = cleanedIds.join(",");
  const base = String(API_BASE_URL || "").replace(/\/+$/, "");

  const url =
    `${base}/question/${encodeURIComponent(subject)}/${encodeURIComponent(difficulty)}` +
    `?exclude_ids=${encodeURIComponent(exclude)}`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      let message = `Không tải được câu hỏi (${response.status})`;

      try {
        const errorData = await response.json();
        if (errorData?.detail) {
          message = errorData.detail;
        }
      } catch (_) {}

      throw new Error(message);
    }

    return await response.json();
  } catch (error) {
    console.error("getQuestion error:", error);
    console.error("API_BASE_URL:", API_BASE_URL);
    console.error("Request URL:", url);
    throw error;
  }
}