const state = {
  datasets: [],
  currentResult: null,
  compareResult: null,
  uploadedDataset: null,
  uploadedFileName: "",
  runtime: null
};

function fetchJSON(url, options = {}) {
  return fetch(url, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  }).then(async (response) => {
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed: ${response.status}`);
    }
    return response.json();
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function setStatus(message, type = "neutral") {
  const node = document.getElementById("status-line");
  node.textContent = message;
  node.dataset.state = type;
}

function humanizeAnalysisMode(mode) {
  const mapping = {
    mock: "规则抽取（mock）",
    hybrid_llm: "规则抽取 + LLM 生成",
    mock_fallback: "LLM 调用失败，已回退 mock"
  };

  return mapping[mode] || "未知模式";
}

function renderRuntimeStatus(runtime = {}, warnings = []) {
  const modeText = humanizeAnalysisMode(runtime.analysis_mode || "mock");
  const modelText = runtime.model_name || "未接入";
  document.getElementById("runtime-mode-banner").textContent = modeText;
  document.getElementById("runtime-model-banner").textContent = modelText;
  document.getElementById("analysis-mode-label").textContent = modeText;
  document.getElementById("runtime-model-label").textContent = modelText;

  const warningNode = document.getElementById("runtime-warning");
  if (warnings.length) {
    warningNode.textContent = warnings.join("；");
  } else if (runtime.analysis_mode === "hybrid_llm") {
    warningNode.textContent = `当前已启用真实模型：${modelText}。主题抽取仍走结构化流程，内容层由 LLM 辅助生成。`;
  } else {
    warningNode.textContent = "当前使用本地 mock 结果，接入 OPENAI_API_KEY 后会自动启用混合模式。";
  }
}

function emptyState(message) {
  return `<div class="empty-state">${escapeHtml(message)}</div>`;
}

function renderCitations(citations = []) {
  if (!citations.length) {
    return `<div class="citations"><span class="citation-tag muted">暂无引用</span></div>`;
  }

  return `
    <div class="citations">
      ${citations
        .map(
          (id) =>
            `<button type="button" class="citation-tag clickable" data-review-id="${escapeHtml(id)}">${escapeHtml(
              id
            )}</button>`
        )
        .join("")}
    </div>
  `;
}

function renderQuestions(result) {
  const container = document.getElementById("question-list");
  const items = result.summary.key_questions || [];
  if (!items.length) {
    container.innerHTML = emptyState("当前版本没有输出关键问题。");
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="question-item">
          <strong>${escapeHtml(item.question)}</strong>
          <p>${escapeHtml(item.summary)}</p>
          ${renderCitations(item.citations)}
        </article>
      `
    )
    .join("");
}

function renderThemes(containerId, items, isNegative = false) {
  const container = document.getElementById(containerId);
  if (!items.length) {
    container.innerHTML = emptyState("当前版本没有可展示的主题。");
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="chip ${isNegative ? "negative" : ""}">
          <div class="chip-title">
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.count)} 条提及</span>
          </div>
          <p>${escapeHtml(item.summary)}</p>
          ${renderCitations(item.citations)}
        </article>
      `
    )
    .join("");
}

function renderStack(containerId, items, titleKey, contentKey, emptyMessage) {
  const container = document.getElementById(containerId);
  if (!items.length) {
    container.innerHTML = emptyState(emptyMessage);
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="stack-item">
          <strong>${escapeHtml(item[titleKey])}</strong>
          <p>${escapeHtml(item[contentKey])}</p>
          ${renderCitations(item.citations)}
        </article>
      `
    )
    .join("");
}

function renderOverview(result) {
  const overview = result.overview || {};
  document.getElementById("overview-headline").textContent = overview.headline || "--";
  document.getElementById("overview-text").textContent = overview.executive_summary || "--";

  const metrics = [
    ["评论数量", overview.review_count ?? "--"],
    ["核心机会", overview.top_positive_label ?? "--"],
    ["核心风险", overview.top_negative_label ?? "--"],
    ["推荐角度", overview.highlighted_selling_point ?? "--"]
  ];

  document.getElementById("overview-metrics").innerHTML = metrics
    .map(
      ([label, value]) => `
        <article class="mini-metric">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `
    )
    .join("");
}

function renderSourceReviews(result) {
  const container = document.getElementById("source-review-list");
  const reviews = result.source_reviews || [];
  if (!reviews.length) {
    container.innerHTML = emptyState("当前没有可展示的原始评论。");
    return;
  }

  container.innerHTML = reviews
    .map(
      (review) => `
        <article class="review-card">
          <div class="review-meta">
            <strong>${escapeHtml(review.review_id)}</strong>
            <span>${review.rating ? `${escapeHtml(review.rating)} / 5 分` : "无评分"}</span>
            <span>${escapeHtml(review.created_at || "日期未知")}</span>
          </div>
          <p>${escapeHtml(review.content)}</p>
          <div class="citations">
            <button type="button" class="citation-tag clickable" data-review-id="${escapeHtml(review.review_id)}">
              查看原文
            </button>
          </div>
        </article>
      `
    )
    .join("");
}

function renderMetrics(result) {
  const metrics = [
    ["引用覆盖率", `${Math.round(result.evaluation.citation_coverage * 100)}%`],
    ["结构完整度", `${Math.round(result.evaluation.structure_completeness * 100)}%`],
    ["可用性评分", result.evaluation.human_usable_score.toFixed(1)],
    ["可信度评分", result.evaluation.trust_score.toFixed(1)]
  ];

  const container = document.getElementById("metrics-grid");
  container.innerHTML = metrics
    .map(
      ([label, value]) => `
        <article class="metric-card">
          <span>${label}</span>
          <strong>${value}</strong>
        </article>
      `
    )
    .join("");
}

function renderCompare(compareResult) {
  const section = document.getElementById("compare-section");
  const winner = document.getElementById("compare-winner");
  const grid = document.getElementById("compare-grid");

  section.hidden = false;
  winner.textContent =
    compareResult.winner === "tie"
      ? "当前轻量评估下，两套提示词表现相同。"
      : `当前胜出方案：${compareResult.winner}`;

  const variants = [compareResult.left, compareResult.right];
  grid.innerHTML = variants
    .map((variant) => {
      const result = variant.result;
      return `
        <article class="compare-card">
          <div class="compare-head">
            <h3>${result.metadata.workflow_label}</h3>
            <span>${variant.prompt_version}</span>
          </div>
          <p>${result.metadata.workflow_description}</p>
          <div class="compare-metrics">
            <div>
              <span>引用覆盖率</span>
              <strong>${Math.round(result.evaluation.citation_coverage * 100)}%</strong>
            </div>
            <div>
              <span>结构完整度</span>
              <strong>${Math.round(result.evaluation.structure_completeness * 100)}%</strong>
            </div>
            <div>
              <span>输出问题数</span>
              <strong>${result.summary.key_questions.length}</strong>
            </div>
            <div>
              <span>优化建议数</span>
              <strong>${result.assets.optimization_suggestions.length}</strong>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderResult(result) {
  state.currentResult = result;
  state.runtime = {
    analysis_mode: result.metadata.analysis_mode,
    model_name: result.metadata.model_name
  };
  document.getElementById("product-name").textContent = result.product_name;
  document.getElementById("workflow-label").textContent = result.metadata.workflow_label;
  document.getElementById("analysis-mode-label").textContent = humanizeAnalysisMode(result.metadata.analysis_mode);
  document.getElementById("runtime-model-label").textContent = result.metadata.model_name || "未接入";
  document.getElementById("citation-coverage").textContent = `${Math.round(
    result.evaluation.citation_coverage * 100
  )}%`;
  document.getElementById("data-source-label").textContent = state.uploadedDataset
    ? `已上传：${state.uploadedFileName}`
    : "内置样例";
  renderRuntimeStatus(state.runtime, result.metadata.warnings || []);

  renderOverview(result);
  renderSourceReviews(result);
  renderQuestions(result);
  renderThemes("positive-themes", result.summary.top_positive_themes);
  renderThemes("negative-themes", result.summary.top_negative_themes, true);
  renderStack("selling-points", result.assets.selling_points, "title", "content", "当前版本没有输出卖点建议。");
  renderStack("faq-list", result.assets.faqs, "question", "answer", "当前版本没有 FAQ 草案。");
  renderStack(
    "optimization-list",
    result.assets.optimization_suggestions,
    "title",
    "content",
    "这个 prompt 版本没有稳定输出优化建议。"
  );
  renderMetrics(result);
}

function normalizeUploadedDataset(input, fileName) {
  const raw = Array.isArray(input) ? { reviews: input } : input;
  if (!raw || typeof raw !== "object" || !Array.isArray(raw.reviews)) {
    throw new Error("上传的 JSON 需要是包含 reviews 数组的对象，或直接是评论数组。");
  }

  const productName = raw.product_name || fileName.replace(/\.json$/i, "") || "上传商品";
  const datasetId = raw.dataset_id || `uploaded-${Date.now()}`;
  const reviews = raw.reviews
    .filter((review) => review && typeof review.content === "string" && review.content.trim())
    .map((review, index) => ({
      product_id: review.product_id || datasetId,
      review_id: review.review_id || `u${String(index + 1).padStart(3, "0")}`,
      rating: review.rating ?? null,
      content: review.content.trim(),
      created_at: review.created_at || ""
    }));

  if (!reviews.length) {
    throw new Error("上传的 JSON 里没有有效的评论内容。");
  }

  return {
    dataset_id: datasetId,
    product_name: productName,
    reviews
  };
}

function buildDatasetPayload(extraPayload = {}) {
  if (state.uploadedDataset) {
    return {
      ...extraPayload,
      dataset: state.uploadedDataset
    };
  }

  return {
    ...extraPayload,
    dataset_id: document.getElementById("dataset-select").value
  };
}

async function loadDatasets() {
  const payload = await fetchJSON("/api/datasets");
  state.datasets = payload.datasets;
  const select = document.getElementById("dataset-select");
  select.innerHTML = payload.datasets
    .map((dataset) => `<option value="${dataset.id}">${dataset.name}（${dataset.review_count} 条评论）</option>`)
    .join("");
}

async function loadRuntimeStatus() {
  const payload = await fetchJSON("/api/health");
  state.runtime = payload.runtime || null;
  renderRuntimeStatus(state.runtime || {});
}

async function runAnalysis() {
  const promptVersion = document.getElementById("prompt-select").value;
  setStatus("正在运行分析...", "loading");

  const result = await fetchJSON("/api/analyze", {
    method: "POST",
    body: JSON.stringify(buildDatasetPayload({ prompt_version: promptVersion }))
  });

  renderResult(result);
  const warnings = result.metadata.warnings || [];
  if (warnings.length) {
    setStatus(`已生成 ${result.product_name} 的分析结果，但模型调用失败并已回退为 mock。`, "neutral");
  } else {
    setStatus(`已生成 ${result.product_name} 的 ${result.metadata.workflow_label} 分析结果。`, "success");
  }
}

async function runCompare() {
  setStatus("正在比较两套提示词工作流...", "loading");

  const result = await fetchJSON("/api/evaluate", {
    method: "POST",
    body: JSON.stringify(buildDatasetPayload({
      left_prompt_version: "v1",
      right_prompt_version: "v2"
    }))
  });

  state.compareResult = result;
  renderCompare(result);
  const leftWarnings = result.left?.result?.metadata?.warnings || [];
  const rightWarnings = result.right?.result?.metadata?.warnings || [];
  if (leftWarnings.length || rightWarnings.length) {
    setStatus("提示词对比已更新，其中至少一侧因模型调用失败回退为 mock。", "neutral");
  } else {
    setStatus("提示词对比结果已更新。", "success");
  }
}

function openCitationDrawer(reviewId) {
  const review = state.currentResult?.review_lookup?.[reviewId];
  if (!review) {
    setStatus(`未找到引用 ${reviewId} 对应的原始评论。`, "error");
    return;
  }

  document.getElementById("drawer-review-id").textContent = review.review_id;
  document.getElementById("drawer-rating").textContent = review.rating ? `评分：${review.rating} / 5` : "评分：暂无";
  document.getElementById("drawer-date").textContent = review.created_at || "日期：未知";
  document.getElementById("drawer-content").textContent = review.content;
  document.getElementById("drawer-shell").hidden = false;
}

function closeCitationDrawer() {
  document.getElementById("drawer-shell").hidden = true;
}

function attachEvents() {
  document.getElementById("analysis-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await runAnalysis();
    } catch (error) {
      setStatus(`分析失败：${error.message}`, "error");
    }
  });

  document.getElementById("compare-btn").addEventListener("click", async () => {
    try {
      await runCompare();
    } catch (error) {
      setStatus(`对比失败：${error.message}`, "error");
    }
  });

  document.getElementById("dataset-file").addEventListener("change", async (event) => {
    const [file] = event.target.files || [];
    if (!file) {
      return;
    }

    try {
      const rawText = await file.text();
      const parsed = JSON.parse(rawText);
      state.uploadedDataset = normalizeUploadedDataset(parsed, file.name);
      state.uploadedFileName = file.name;
      document.getElementById("source-status").textContent = `已加载 ${file.name}，后续分析会优先使用这份上传数据。`;
      setStatus(`已上传 ${file.name}，正在运行分析...`, "loading");
      await runAnalysis();
    } catch (error) {
      state.uploadedDataset = null;
      state.uploadedFileName = "";
      document.getElementById("source-status").textContent = "上传失败，请检查 JSON 结构是否包含 reviews 数组。";
      setStatus(`上传失败：${error.message}`, "error");
    }
  });

  document.getElementById("clear-upload-btn").addEventListener("click", async () => {
    state.uploadedDataset = null;
    state.uploadedFileName = "";
    document.getElementById("dataset-file").value = "";
    document.getElementById("source-status").textContent =
      "当前使用内置样例数据。上传 JSON 后会优先分析你自己的评论数据。";
    try {
      await runAnalysis();
    } catch (error) {
      setStatus(`重新加载样例失败：${error.message}`, "error");
    }
  });

  document.body.addEventListener("click", (event) => {
    const citationButton = event.target.closest("[data-review-id]");
    if (citationButton) {
      openCitationDrawer(citationButton.dataset.reviewId);
      return;
    }

    if (event.target.id === "drawer-close" || event.target.id === "drawer-backdrop") {
      closeCitationDrawer();
    }
  });
}

async function bootstrap() {
  attachEvents();
  setStatus("正在加载数据集...", "loading");

  try {
    await loadRuntimeStatus();
    await loadDatasets();
    document.getElementById("prompt-select").value = "v2";
    await runAnalysis();
  } catch (error) {
    setStatus(`初始化失败：${error.message}`, "error");
  }
}

bootstrap();
