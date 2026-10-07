// Keep labels outside the tool-to-agent routes, including growing candidate rings.
export function layoutActivityLabels(root: HTMLElement) {
  const svg = root.querySelector<SVGSVGElement>(".nv-activity-map");
  if (!svg) return;
  const center = svg.querySelector(".nv-activity-core")?.parentElement;
  const centerY =
    (center as unknown as SVGGElement)?.transform.baseVal.consolidate()?.matrix
      .f ?? 245;
  for (const tool of svg.querySelectorAll<SVGCircleElement>(
    ".nv-activity-tool",
  )) {
    const group = tool.parentNode as SVGGElement;
    const y = group.transform.baseVal.consolidate()?.matrix.f ?? centerY;
    const radius = Math.max(
      ...Array.from(
        group.querySelectorAll("circle"),
        (circle) => circle.r.baseVal.value,
      ),
    );
    const above = y < centerY;
    group
      .querySelector(".nv-activity-label")
      ?.setAttribute("y", String(above ? -radius - 32 : radius + 32));
    group
      .querySelector(".nv-activity-caption")
      ?.setAttribute("y", String(above ? -radius - 12 : radius + 52));
  }
  // Long labels and future outer rings must remain inside the SVG viewport.
  const bounds = svg.getBBox(),
    view = svg.viewBox.baseVal;
  const left = Math.min(view.x, bounds.x - 16),
    top = Math.min(view.y, bounds.y - 16);
  const right = Math.max(view.x + view.width, bounds.x + bounds.width + 16);
  const bottom = Math.max(view.y + view.height, bounds.y + bounds.height + 16);
  svg.setAttribute("viewBox", `${left} ${top} ${right - left} ${bottom - top}`);
}
