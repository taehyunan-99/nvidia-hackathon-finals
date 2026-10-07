import {
  initialConditions,
  interestLabels,
  gradeLabels,
  type Conditions,
} from "./contract";
const key = "duru:conditions:v1";
export function readConditions(): Conditions {
  try {
    const value = JSON.parse(sessionStorage.getItem(key) || "null");
    if (
      !value ||
      !Array.isArray(value.interests) ||
      !value.interests.every((v: string) => Object.hasOwn(interestLabels, v)) ||
      !Array.isArray(value.grades) ||
      !value.grades.every((v: string) => Object.hasOwn(gradeLabels, v)) ||
      !["unknown", "0", "1", "2+"].includes(value.guardians) ||
      !["all", "jongno", "jung"].includes(value.district) ||
      ![null, "2026-10-10", "2026-10-11", "2026-10-17", "2026-10-18"].includes(
        value.date,
      )
    )
      return initialConditions;
    return {
      interests: value.interests,
      grades: value.grades,
      guardians: value.guardians,
      date: value.date,
      district: value.district,
    };
  } catch {
    return initialConditions;
  }
}
export function saveConditions(value: Conditions) {
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* In-memory navigation still works when storage is unavailable. */
  }
}
