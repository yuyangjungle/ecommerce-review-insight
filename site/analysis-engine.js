const POSITIVE_RULES = {
  battery_life: {
    label: "续航表现",
    priority: 1,
    keywords: ["续航", "通勤", "一天"],
    summary: "用户反复提到日常通勤和整天使用场景下的续航表现稳定。",
    selling_point: "突出全天续航能力，覆盖通勤和轻运动场景。",
    copy: "全天通勤不断电，日常出门更省心。",
    faq: {
      question: "一天一充够吗？",
      answer: "从评论来看，多数用户认为日常通勤场景基本可以满足一天使用。"
    }
  },
  comfort: {
    label: "佩戴舒适度",
    priority: 2,
    keywords: ["舒服", "舒适", "不疼", "运动", "不容易掉"],
    summary: "佩戴体验稳定，长时间使用和运动场景下都有正向反馈。",
    selling_point: "强调长时间佩戴舒适和运动时稳固不易脱落。",
    copy: "久戴不压耳，运动通勤都稳稳贴合。",
    faq: {
      question: "运动时容易掉吗？",
      answer: "现有评论显示，大多数用户认为佩戴较稳，运动时不易脱落。"
    }
  },
  portability: {
    label: "便携与外观",
    priority: 3,
    keywords: ["小巧", "很小", "方便", "口袋", "好看", "外观", "便携"],
    summary: "评论对充电盒便携性和外观设计认可度较高。",
    selling_point: "突出小巧便携和外观设计感，适合日常携带。",
    copy: "小巧充电盒随手装进口袋，轻装出门更方便。",
    faq: {
      question: "充电盒便携吗？",
      answer: "不少用户提到充电盒体积小，放入口袋或随身包里都很方便。"
    }
  },
  fast_connection: {
    label: "连接速度",
    priority: 4,
    keywords: ["秒连", "连接速度", "连接快", "拿出来"],
    summary: "用户对耳机拿出即连的连接速度反馈较好。",
    selling_point: "强调开盖即连和日常切换设备时的效率体验。",
    copy: "拿起即连，碎片化使用也不用等。",
    faq: {
      question: "连接速度快吗？",
      answer: "从样本评论看，连接速度是明显的正向体验点。"
    }
  }
};

const NEGATIVE_RULES = {
  connection_stability: {
    label: "连接稳定性",
    priority: 1,
    keywords: ["断连", "地铁"],
    summary: "复杂环境下存在偶发断连问题，影响连续使用体验。",
    optimization: "优先优化复杂通勤环境下的蓝牙连接稳定性。",
    question: "地铁等复杂环境会不会断连？"
  },
  noise_cancellation: {
    label: "降噪落差",
    priority: 3,
    keywords: ["降噪", "宣传比", "差一些"],
    summary: "用户认可有一定降噪效果，但对宣传预期与实际体验存在落差。",
    optimization: "优化降噪能力表达，减少宣传与实际体验之间的心理落差。",
    question: "降噪效果和宣传一致吗？"
  },
  microphone: {
    label: "通话收音稳定性",
    priority: 2,
    keywords: ["麦克风", "收音", "开会", "声音忽大忽小"],
    summary: "通话场景中收音稳定性不足，影响远程会议体验。",
    optimization: "提升麦克风收音的一致性与会议场景适配能力。",
    question: "开会通话时收音稳定吗？"
  },
  sound_quality: {
    label: "音质期待管理",
    priority: 4,
    keywords: ["音质一般"],
    summary: "部分评论认为音质表现中规中矩，未形成明显惊喜。",
    optimization: "在内容表达上避免对音质做过度承诺，聚焦更强势卖点。",
    question: "音质是不是核心卖点？"
  }
};

export const PROMPT_CONFIGS = {
  v1: {
    label: "v1 直接总结工作流",
    description: "直接总结评论内容，结构较轻，引用覆盖不稳定。"
  },
  v2: {
    label: "v2 主题优先工作流",
    description: "先抽取主题再生成内容，并显式保留引用依据。"
  }
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function normalizeDataset(dataset) {
  const normalized = clone(dataset);
  normalized.dataset_id = normalized.dataset_id || "uploaded-dataset";
  normalized.product_name = normalized.product_name || "上传商品";
  normalized.reviews = Array.isArray(normalized.reviews) ? normalized.reviews : [];
  return normalized;
}

function dedupe(items) {
  const seen = new Set();
  const result = [];

  for (const item of items) {
    if (!seen.has(item)) {
      seen.add(item);
      result.push(item);
    }
  }

  return result;
}

function collectThemes(reviews, rules, themeType) {
  const bucket = {};

  for (const review of reviews) {
    const text = review.content || "";
    for (const [themeId, rule] of Object.entries(rules)) {
      if (!rule.keywords.some((keyword) => text.includes(keyword))) {
        continue;
      }

      const entry =
        bucket[themeId] ||
        (bucket[themeId] = {
          theme_id: themeId,
          title: rule.label,
          priority: rule.priority,
          type: themeType,
          summary: rule.summary,
          count: 0,
          citations: [],
          snippets: []
        });

      entry.count += 1;
      entry.citations.push(review.review_id);
      entry.snippets.push(review.content);
    }
  }

  const themes = Object.values(bucket)
    .map((item) => ({
      ...item,
      citations: dedupe(item.citations).slice(0, 3),
      snippets: item.snippets.slice(0, 2)
    }))
    .sort((left, right) => {
      if (left.count !== right.count) {
        return right.count - left.count;
      }
      if (left.priority !== right.priority) {
        return left.priority - right.priority;
      }
      return left.title.localeCompare(right.title, "zh-CN");
    })
    .map(({ priority, ...rest }) => rest);

  return themes;
}

function buildKeyQuestions(positiveThemes, negativeThemes) {
  const questions = [];

  for (const theme of negativeThemes) {
    const rule = NEGATIVE_RULES[theme.theme_id];
    questions.push({
      question: rule.question,
      summary: theme.summary,
      citations: theme.citations
    });
  }

  for (const theme of positiveThemes) {
    const rule = POSITIVE_RULES[theme.theme_id];
    questions.push({
      question: rule.faq.question,
      summary: theme.summary,
      citations: theme.citations
    });
  }

  return questions.slice(0, 3);
}

function buildAssets(positiveThemes, negativeThemes) {
  const sellingPoints = [];
  const copySuggestions = [];
  const faqs = [];
  const optimizationSuggestions = [];

  for (const theme of positiveThemes.slice(0, 3)) {
    const rule = POSITIVE_RULES[theme.theme_id];
    sellingPoints.push({
      title: theme.title,
      content: rule.selling_point,
      citations: theme.citations
    });
    copySuggestions.push({
      title: `${theme.title}文案建议`,
      content: rule.copy,
      citations: theme.citations
    });
    faqs.push({
      question: rule.faq.question,
      answer: rule.faq.answer,
      citations: theme.citations
    });
  }

  for (const theme of negativeThemes.slice(0, 3)) {
    const rule = NEGATIVE_RULES[theme.theme_id];
    optimizationSuggestions.push({
      title: theme.title,
      content: rule.optimization,
      citations: theme.citations
    });
  }

  return {
    selling_points: sellingPoints,
    copy_suggestions: copySuggestions,
    faqs,
    optimization_suggestions: optimizationSuggestions
  };
}

function calculateEvaluation(positiveThemes, negativeThemes, assets) {
  const sections = [
    positiveThemes,
    negativeThemes,
    assets.selling_points,
    assets.copy_suggestions,
    assets.faqs,
    assets.optimization_suggestions
  ];

  const structureCompleteness = Number(
    (sections.filter((section) => section.length > 0).length / sections.length).toFixed(2)
  );

  let citedItems = 0;
  let totalItems = 0;

  for (const section of sections) {
    for (const item of section) {
      totalItems += 1;
      if (item.citations && item.citations.length) {
        citedItems += 1;
      }
    }
  }

  const citationCoverage = totalItems ? Number((citedItems / totalItems).toFixed(2)) : 0;
  const humanUsableScore = Number((3.2 + structureCompleteness * 0.8 + citationCoverage * 0.5).toFixed(2));
  const trustScore = Number((3.0 + citationCoverage).toFixed(2));

  return {
    structure_completeness: structureCompleteness,
    citation_coverage: citationCoverage,
    human_usable_score: humanUsableScore,
    trust_score: trustScore
  };
}

function buildReviewLookup(reviews) {
  const lookup = {};

  for (const review of reviews) {
    lookup[review.review_id] = {
      review_id: review.review_id,
      content: review.content,
      rating: review.rating ?? null,
      created_at: review.created_at || ""
    };
  }

  return lookup;
}

function buildOverview(productName, positiveThemes, negativeThemes, assets, reviewCount) {
  const topPositive = positiveThemes[0]?.title || "暂无明显正向主题";
  const topNegative = negativeThemes[0]?.title || "暂无明显负向主题";
  const keyCopy = assets.selling_points[0]?.content || "暂无推荐卖点";

  return {
    headline: `${productName} 的核心机会在 ${topPositive}，主要风险集中在 ${topNegative}。`,
    executive_summary: `系统基于 ${reviewCount} 条评论完成主题抽取与内容生成，当前建议优先放大“${topPositive}”相关卖点，同时关注“${topNegative}”带来的体验落差。`,
    highlighted_selling_point: keyCopy,
    top_positive_label: topPositive,
    top_negative_label: topNegative,
    review_count: reviewCount
  };
}

function applyPromptVersion(baseResult, promptVersion) {
  if (!PROMPT_CONFIGS[promptVersion]) {
    throw new Error(`Unsupported prompt version: ${promptVersion}`);
  }

  const result = clone(baseResult);
  result.metadata = {
    prompt_version: promptVersion,
    workflow_label: PROMPT_CONFIGS[promptVersion].label,
    workflow_description: PROMPT_CONFIGS[promptVersion].description
  };

  if (promptVersion === "v1") {
    result.summary.top_positive_themes = result.summary.top_positive_themes.slice(0, 3);
    result.summary.top_negative_themes = result.summary.top_negative_themes.slice(0, 2);
    result.summary.key_questions = result.summary.key_questions.slice(0, 2);
    result.assets.copy_suggestions = result.assets.copy_suggestions.slice(0, 2);
    result.assets.optimization_suggestions = [];

    if (result.assets.selling_points[1]) {
      result.assets.selling_points[1].citations = [];
    }
    if (result.assets.faqs[1]) {
      result.assets.faqs[1].citations = [];
    }
    if (result.summary.key_questions.length) {
      result.summary.key_questions[result.summary.key_questions.length - 1].citations = [];
    }
  }

  result.evaluation = calculateEvaluation(
    result.summary.top_positive_themes,
    result.summary.top_negative_themes,
    result.assets
  );

  return result;
}

export function analyzeDataset(dataset, promptVersion = "v2") {
  const normalizedDataset = normalizeDataset(dataset);
  const reviews = normalizedDataset.reviews;
  const positiveThemes = collectThemes(reviews, POSITIVE_RULES, "positive_theme");
  const negativeThemes = collectThemes(reviews, NEGATIVE_RULES, "negative_theme");
  const keyQuestions = buildKeyQuestions(positiveThemes, negativeThemes);
  const assets = buildAssets(positiveThemes, negativeThemes);
  const reviewLookup = buildReviewLookup(reviews);
  const overview = buildOverview(
    normalizedDataset.product_name,
    positiveThemes,
    negativeThemes,
    assets,
    reviews.length
  );

  const baseResult = {
    dataset_id: normalizedDataset.dataset_id,
    product_name: normalizedDataset.product_name,
    overview,
    review_lookup: reviewLookup,
    source_reviews: reviews.slice(0, 8),
    summary: {
      top_positive_themes: positiveThemes,
      top_negative_themes: negativeThemes,
      key_questions: keyQuestions
    },
    assets
  };

  return applyPromptVersion(baseResult, promptVersion);
}

export function evaluatePromptVersions(dataset, leftPromptVersion, rightPromptVersion) {
  const leftResult = analyzeDataset(dataset, leftPromptVersion);
  const rightResult = analyzeDataset(dataset, rightPromptVersion);
  const leftScore = leftResult.evaluation.human_usable_score + leftResult.evaluation.trust_score;
  const rightScore = rightResult.evaluation.human_usable_score + rightResult.evaluation.trust_score;

  return {
    dataset_id: normalizeDataset(dataset).dataset_id,
    winner: leftScore === rightScore ? "tie" : leftScore > rightScore ? leftPromptVersion : rightPromptVersion,
    left: {
      prompt_version: leftPromptVersion,
      result: leftResult,
      scores: leftResult.evaluation
    },
    right: {
      prompt_version: rightPromptVersion,
      result: rightResult,
      scores: rightResult.evaluation
    }
  };
}
