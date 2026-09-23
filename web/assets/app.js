const $ = (selector) => document.querySelector(selector);

async function getJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "요청에 실패했습니다.");
  }
  return data;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render(target, data, type = "default") {
  target.classList.remove("loading", "error");
  if (type === "question") {
    target.innerHTML = renderQuestion(data);
  } else if (type === "today") {
    target.innerHTML = renderToday(data);
  } else if (type === "vault") {
    target.innerHTML = renderVault(data);
  } else if (type === "catalog") {
    target.innerHTML = renderCatalog(data);
  } else if (type === "record") {
    target.innerHTML = renderRecord(data);
  } else if (type === "config") {
    target.innerHTML = renderConfig(data);
  } else {
    target.textContent = JSON.stringify(data, null, 2);
  }
}

function renderQuestion(data) {
  const explanation = data.explanation || {};
  const observation = data.observationPlan || {};
  const experiments = data.experimentSuggestions || [];
  const related = data.relatedQuestions || [];
  return `
    <div class="answer-head">
      <span class="eyebrow">${escapeHtml(data.interpretedTopic || "탐구")}</span>
      <span class="confidence">확신도 ${Math.round((data.confidence || 0) * 100)}%</span>
    </div>
    <p class="answer">${escapeHtml(data.answerPreview || explanation.explanation || "답변을 준비했어요.")}</p>
    ${explanation.explanation ? `<div class="answer-block"><strong>조금 더 알아보기</strong><p>${escapeHtml(explanation.explanation)}</p></div>` : ""}
    ${observation.whatToObserve ? `<div class="answer-block"><strong>직접 관찰해보기</strong><p>${escapeHtml(observation.whatToObserve)}</p><small>${escapeHtml(observation.method || "")}</small></div>` : ""}
    ${experiments.length ? `<div class="answer-block"><strong>추천 실험</strong><ul>${experiments.slice(0, 2).map((item) => `<li><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.purpose || "")}</span></li>`).join("")}</ul></div>` : ""}
    ${related.length ? `<div class="related"><strong>이어서 궁금해할 질문</strong><div class="chips">${related.slice(0, 4).map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div></div>` : ""}
  `;
}

function renderToday(data) {
  return (data.items || []).map((item) => `
    <div class="today-card">
      <span class="eyebrow">오늘의 ${escapeHtml(item.category || "탐구")}</span>
      <h3>${escapeHtml(item.question)}</h3>
      <p>${escapeHtml(item.reason || "오늘 바로 살펴보기 좋은 질문이에요.")}</p>
      <div class="action-row">${(item.availableActions || []).map((action) => `<button type="button" class="small-action" data-today-action="${escapeHtml(action)}" data-today-question="${escapeHtml(item.question)}">${escapeHtml(action)}</button>`).join("")}</div>
    </div>
  `).join("") || emptyState("오늘의 질문을 준비하지 못했어요.");
}

function renderVault(data) {
  if (!data.entries?.length) return emptyState("아직 보관한 궁금증이 없어요.");
  return `<div class="count-label">${data.count}개의 궁금증</div><div class="entry-list">${data.entries.slice(0, 8).map((item) => `
    <article class="entry"><div><span class="eyebrow">${escapeHtml(item.category)} · ${escapeHtml(item.topic)}</span><h3>${escapeHtml(item.question)}</h3><p>${escapeHtml(item.aiAnswer)}</p></div></article>
  `).join("")}</div>`;
}

function renderCatalog(data) {
  return (data.catalog || []).map((field) => `
    <section class="catalog-field"><div class="field-title"><strong>${escapeHtml(field.fieldName)}</strong><span>${(field.discoveredPrinciples || []).length}개 발견</span></div><div class="chips">${(field.baselinePrinciples || []).map((item) => `<span>${escapeHtml(item)}</span>`).join("")}${(field.discoveredPrinciples || []).map((item) => `<span class="discovered">${escapeHtml(item.principle)}</span>`).join("")}</div></section>
  `).join("");
}

function renderRecord(data) {
  return `<div class="stat-grid"><div><strong>${data.solvedCuriosityCount || 0}</strong><span>해결한 궁금증</span></div><div><strong>${data.completedExperimentCount || 0}</strong><span>완료한 실험</span></div><div><strong>${data.discoveredPrincipleCount || 0}</strong><span>발견한 원리</span></div><div><strong>${data.consecutiveExplorationDays || 0}</strong><span>연속 탐험 일수</span></div></div><div class="record-footer">탐험 분야: ${escapeHtml((data.exploredCategories || []).join(" · ") || "아직 없음")}</div>`;
}

function renderConfig(data) {
  return `<div class="status-row"><span>연결 방식</span><strong>${escapeHtml(data.provider || "generic")}</strong></div><div class="status-row"><span>Azure OpenAI</span><strong class="${data.azureOpenAIConfigured ? "is-on" : "is-off"}">${data.azureOpenAIConfigured ? "연결 준비됨" : "설정 필요"}</strong></div><p class="hint">키 값은 보안을 위해 화면에 표시하지 않아요.</p>`;
}

function emptyState(message) {
  return `<div class="empty-state">${escapeHtml(message)}</div>`;
}

$("#ask-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const resultEl = $("#ask-result");
  resultEl.textContent = "불러오는 중...";

  try {
    const questionText = $("#question").value.trim();
    const level = $("#level").value;
    const data = await getJson("/api/v1/questions/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionText, level }),
    });
    render(resultEl, data, "question");
  } catch (error) {
    resultEl.textContent = error.message;
  }
});

$("#today-btn").addEventListener("click", async () => {
  const el = $("#today-result");
  el.textContent = "불러오는 중...";
  try {
    const data = await getJson("/api/v1/today?limit=1");
    render(el, data, "today");
  } catch (error) {
    el.textContent = error.message;
  }
});

$("#today-result").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-today-action]");
  if (!button) return;

  const resultEl = $("#today-result");
  resultEl.classList.add("loading");
  try {
    const data = await getJson("/api/v1/today/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        questionText: button.dataset.todayQuestion,
        action: button.dataset.todayAction,
        level: $("#level").value,
      }),
    });
    resultEl.innerHTML = button.dataset.todayAction === "알아보기"
      ? renderQuestion(data.result || data)
      : renderTodayAction(data);
  } catch (error) {
    resultEl.classList.add("error");
    resultEl.textContent = error.message;
  } finally {
    resultEl.classList.remove("loading");
  }
});

function renderTodayAction(data) {
  const observation = data.observationPlan || {};
  const experiments = data.experimentSuggestions?.experiments || [];
  return `<div class="answer-block"><strong>관찰할 것</strong><p>${escapeHtml(observation.plan?.whatToObserve || "주변의 변화를 살펴보세요.")}</p><small>${escapeHtml(observation.plan?.method || "")}</small></div>${experiments.length ? `<div class="answer-block"><strong>해볼 실험</strong><ul>${experiments.map((item) => `<li><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.purpose || "")}</span></li>`).join("")}</ul></div>` : ""}`;
}

$("#vault-btn").addEventListener("click", async () => {
  const el = $("#vault-result");
  el.textContent = "불러오는 중...";
  try {
    const data = await getJson("/api/v1/vault");
    render(el, data, "vault");
  } catch (error) {
    el.textContent = error.message;
  }
});

$("#catalog-btn").addEventListener("click", async () => {
  const el = $("#catalog-result");
  el.textContent = "불러오는 중...";
  try {
    const data = await getJson("/api/v1/catalog");
    render(el, data, "catalog");
  } catch (error) {
    el.textContent = error.message;
  }
});

$("#record-btn").addEventListener("click", async () => {
  const el = $("#record-result");
  el.textContent = "불러오는 중...";
  try {
    const data = await getJson("/api/v1/exploration-record");
    render(el, data, "record");
  } catch (error) {
    el.textContent = error.message;
  }
});

$("#config-btn").addEventListener("click", async () => {
  const el = $("#config-result");
  el.textContent = "불러오는 중...";
  try {
    const data = await getJson("/api/config/status");
    render(el, data, "config");
  } catch (error) {
    el.textContent = error.message;
  }
});
