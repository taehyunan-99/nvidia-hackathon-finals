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
      !["unknown", "0", "1", "2", "2+"].includes(value.guardians) ||
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
      children: Array.isArray(value.children) && value.children.length <= 3 && value.children.every((c: NonNullable<Conditions['children']>[number]) =>
        typeof c.member_id === 'string' && (c.grade === null || Object.hasOwn(gradeLabels, c.grade)) &&
        (c.age_years === null || (Number.isInteger(c.age_years.minimum) && c.age_years.minimum >= 0 && c.age_years.minimum <= 18 && c.age_years.maximum === c.age_years.minimum))) ? value.children : null,
      composition_complete: value.composition_complete === true && Array.isArray(value.children),
      delivery_mode: ['in_person', 'online'].includes(value.delivery_mode) ? value.delivery_mode : null,
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
