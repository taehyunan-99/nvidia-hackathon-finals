import { useEffect, useRef, useState } from "react";
import { type AssessedCandidate } from "./contract";

declare global {
  interface Window { navermap_authFailure?: () => void }
}
let sdkPromise: Promise<typeof naver.maps> | undefined;
function loadMaps() {
  if (!sdkPromise) sdkPromise = (async () => {
    const response = await fetch("/api/maps-config");
    if (!response.ok) throw new Error("지도 연결 설정을 확인해 주세요.");
    const { clientId } = await response.json();
    if (typeof clientId !== "string" || !clientId) throw new Error("지도 연결 설정이 없습니다.");
    return new Promise<typeof naver.maps>((resolve, reject) => {
      const script = document.createElement("script");
      const timer = window.setTimeout(() => reject(new Error("지도 연결 시간이 초과됐어요.")), 15000);
      script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${encodeURIComponent(clientId)}`;
      script.onload = () => {
        clearTimeout(timer);
        if (typeof naver !== "undefined" && naver.maps) resolve(naver.maps);
        else reject(new Error("지도를 불러오지 못했어요."));
      };
      script.onerror = () => { clearTimeout(timer); reject(new Error("지도 연결에 실패했어요.")); };
      document.head.append(script);
    });
  })();
  return sdkPromise;
}

export function MapResults({ candidates }: { candidates: AssessedCandidate[] }) {
  const [selected, setSelected] = useState(candidates[0].id);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const container = useRef<HTMLDivElement>(null);
  const markers = useRef<{ id: string; marker: naver.maps.Marker; button: HTMLButtonElement }[]>([]);
  const active = candidates.find(candidate => candidate.id === selected)!;
  const activeIndex = candidates.indexOf(active);
  const cost = active.cost.replace(" · 예시", "");
  const costParts = cost.match(/^(가족당|1인) (.+)$/);

  useEffect(() => {
    let disposed = false;
    let map: naver.maps.Map | undefined;
    const entries: typeof markers.current = [];
    window.navermap_authFailure = () => { if (!disposed) setError("지도 인증에 실패했어요. 허용 주소를 확인해 주세요."); };
    loadMaps().then(maps => {
      if (disposed || !container.current) return;
      map = new maps.Map(container.current, {
        center: new maps.LatLng(37.572, 126.986), zoom: 14,
        zoomControl: true, scrollWheel: false,
        zoomControlOptions: { position: maps.Position.TOP_RIGHT },
      });
      const first = candidates.find(candidate => candidate.testCoordinates)?.testCoordinates;
      const firstPoint = new maps.LatLng(first?.latitude ?? 37.572, first?.longitude ?? 126.986);
      const bounds = new maps.LatLngBounds(firstPoint, firstPoint);
      candidates.forEach((candidate, index) => {
        const coords = candidate.testCoordinates;
        if (!coords) return;
        const position = new maps.LatLng(coords.latitude, coords.longitude);
        bounds.extend(position);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "map-marker";
        button.textContent = String(index + 1);
        button.setAttribute("aria-label", `${index + 1}번 지도 마커: ${candidate.title}`);
        button.addEventListener("click", event => {
          event.stopPropagation();
          setSelected(candidate.id);
        });
        const marker = new maps.Marker({
          map, position, title: candidate.title,
          icon: { content: button, anchor: new maps.Point(20, 20) },
        });
        entries.push({ id: candidate.id, marker, button });
      });
      markers.current = entries;
      if (entries.length > 1) map.fitBounds(bounds, { top: 70, right: 70, bottom: 70, left: 70 });
      setReady(true);
    }).catch(reason => { if (!disposed) setError(reason.message); });
    return () => {
      disposed = true;
      entries.forEach(({ marker }) => marker.setMap(null));
      map?.destroy();
      markers.current = [];
      delete window.navermap_authFailure;
    };
  }, [candidates, attempt]);

  useEffect(() => {
    markers.current.forEach(({ id, marker, button }) => {
      const isSelected = id === selected;
      button.setAttribute("aria-pressed", String(isSelected));
      marker.setZIndex(isSelected ? 100 : 1);
    });
  }, [selected, ready]);

  return <section className="map-results" aria-label="후보와 지도">
    <p className="map-demo-note">공식 자료에 좌표가 있는 후보만 지도에 표시합니다.</p>
    <div className="map-candidate-selector" role="group" aria-label="후보 선택">
      <span>후보 선택</span>
      {candidates.map((candidate, index) => <button key={candidate.id}
        className="nv-button nv-secondary" aria-pressed={selected === candidate.id}
        aria-label={`${index + 1}번 후보 선택: ${candidate.title}`}
        onClick={() => setSelected(candidate.id)}>{index + 1}</button>)}
      <span className="map-candidate-index">{activeIndex + 1} / {candidates.length}</span>
    </div>
    <div className="map-results-layout">
      <div className="map-candidate-list">
        <article
          className="nv-card map-candidate" id={`map-card-${active.id}`}
          data-selected={selected === active.id} key={active.id}
        >
          <div className="section-heading">
            <span className="map-card-number">{activeIndex + 1} · 문화체험</span>
            <span className="eyebrow">공식 자료</span>
          </div>
          <h2 className="map-candidate-title">{active.title}</h2>
          <div className="map-fit-checks" aria-label="가족 조건 확인">
            {active.checks.map(check => <span key={check.label} data-state={check.verdict === "pass" ? "completed" : "hold"}
              title={check.detail}>{check.verdict === "pass" ? "✓" : "!"} {check.label} {check.verdict === "pass" ? "확인" : "확인 필요"}</span>)}
          </div>
          <p className="nv-description">{active.experience}</p>
          <dl className="map-key-facts">
            <div className="map-schedule-insight"><dt>
              <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18m-13 5h2m4 0h2"/></svg>
              <span>일정</span></dt><dd>
              <div className="map-date-options">{active.dates.map(date => <span key={date}>{Number(date.slice(5, 7))}/{Number(date.slice(8))}</span>)}</div>
              <small>{active.time}</small></dd></div>
            <div className="map-cost-insight"><dt>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7V5H5a2 2 0 0 0 0 4h15v12H5a2 2 0 0 1-2-2V7m17 6h-5v4h5"/><circle cx="17" cy="15" r=".6"/></svg>
              <span>참여비</span>{costParts && <span className="map-cost-unit">{costParts[1]}</span>}</dt>
              <dd><strong>{costParts ? costParts[2] : cost}</strong></dd></div>
          </dl>
          <p className="map-place">{active.place}</p>
          <div className="map-next-check">
            <strong>선택 전에 확인</strong>
            {active.checks.filter(check => check.verdict === "unknown").map(check => <p key={check.label}>{check.label} · {check.detail}</p>)}
            <p>실제 운영·잔여석·신청 경로는 아직 확인되지 않았어요.</p>
          </div>
          <details className="map-card-details">
            <summary>대상·준비물·근거 보기</summary>
            <dl><div><dt>참여 대상</dt><dd>{active.checks.find(check => check.label === "학년")?.detail || "참여 대상 미확인"}</dd></div>
              <div><dt>보호자</dt><dd>{active.checks.find(check => check.label === "동반 조건")?.detail || "동반 조건 미확인"}</dd></div>
              <div><dt>준비물</dt><dd>{active.preparation}</dd></div></dl>
            {active.evidence.map(evidence => <div className="map-card-evidence" key={evidence.id}>
              <strong>{evidence.title}</strong><blockquote>{evidence.quote}</blockquote><span>{evidence.source}</span>
            </div>)}
          </details>
          <a className="nv-button nv-secondary" href={active.officialUrl} target="_blank" rel="noopener noreferrer">공식 신청 안내</a>
          <div className="map-card-footer"><span>{active.testCoordinates ? `● ${activeIndex + 1}번 마커와 연결됨` : "위치 좌표 미확인"}</span>
            <span>번호 또는 마커로 후보 전환</span></div>
        </article>
      </div>
      <aside className="map-panel" aria-label="후보 위치 지도">
        <div className="naver-map" ref={container} aria-label="네이버 지도">
          {!ready && !error && <p className="map-message" role="status">지도를 불러오는 중…</p>}
        </div>
        {error && <div className="map-error" role="alert"><p>{error} 후보 목록은 계속 확인할 수 있어요.</p><button className="nv-button nv-secondary" onClick={() => { sdkPromise = undefined; setError(""); setReady(false); setAttempt(value => value + 1); }}>지도 다시 연결</button></div>}
        <div className="map-selection" role="status" aria-live="polite">
          <span className="eyebrow">선택한 후보 · {candidates.indexOf(active) + 1}번</span>
          <strong>{active.title}</strong>
          <span>{active.testCoordinates ? `좌표 ${active.testCoordinates.latitude.toFixed(4)}, ${active.testCoordinates.longitude.toFixed(4)}` : "공식 자료의 위치 좌표 미확인"}</span>
        </div>
      </aside>
    </div>
  </section>;
}
