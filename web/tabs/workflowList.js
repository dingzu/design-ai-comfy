import { isCacheValid, getCachedData, setCachedData, clearCache } from "./workflowList/cache.js";
import { showToast, createWorkflowCard, createEmptyState, createPaginationButton } from "./workflowList/components.js";
import { fetchWorkflows, loadWorkflowToCanvas } from "./workflowList/api.js";
import { setWorkflowsData } from "./workflowList/state.js";

export function renderWorkflowList(el) {
  el.innerHTML = "";

  const container = document.createElement("div");
  container.style.cssText = "display: flex; flex-direction: column; height: 100%; background: #1a1a1a;"

  let workflows = [];
  let filteredWorkflows = [];
  let page = 1;
  let pageSize = parseInt(localStorage.getItem('workflow_pageSize')) || 100;
  let total = 0;
  let totalPages = 0;
  let loading = false;
  let searchKeyword = "";

  const loadWorkflow = (workflow) => {
    try {
      console.log("📂 准备加载工作流:", workflow.name);

      if (loadWorkflowToCanvas(workflow)) {
        if (workflow.taskType) {
          // 如果 taskType 是 defaultWorkflow，则使用 wanVideo 代替
          const actualTaskType = workflow.taskType === 'defaultWorkflow' ? 'wanVideo' : workflow.taskType;

          localStorage.setItem('selectedTaskType', actualTaskType);
          console.log("📋 已保存任务类型:", actualTaskType);

          if (window.updateTaskType) {
            window.updateTaskType(actualTaskType, true);
          }
          showToast(`工作流加载成功 (任务类型: ${actualTaskType})`);
        } else {
          showToast("工作流加载成功");
        }
        console.log("✅ 工作流加载成功:", workflow.name);
      } else {
        console.error("❌ app.loadGraphData 方法不存在");
        alert("加载失败：未找到加载方法");
      }
    } catch (error) {
      console.error("❌ 加载工作流失败:", error);
      alert("加载失败：" + error.message);
    }
  };

  const renderWorkflows = () => {
    const listContainer = document.querySelector("#workflow-list-container");
    if (!listContainer) return;

    listContainer.innerHTML = "";

    const displayWorkflows = searchKeyword ? filteredWorkflows : workflows;

    if (displayWorkflows.length === 0) {
      listContainer.appendChild(createEmptyState());
      return;
    }

    displayWorkflows.forEach((workflow) => {
      const card = createWorkflowCard(workflow, loadWorkflow);
      listContainer.appendChild(card);
    });
  };

  const filterWorkflows = () => {
    if (!searchKeyword) {
      filteredWorkflows = [];
      renderWorkflows();
      return;
    }

    filteredWorkflows = workflows.filter((workflow) => {
      const nameMatch = workflow.name.toLowerCase().includes(searchKeyword);
      const idMatch = workflow.id.toLowerCase().includes(searchKeyword);
      return nameMatch || idMatch;
    });

    renderWorkflows();
  };

  const updatePagination = () => {
    const paginationContainer = document.querySelector("#pagination-container");
    if (!paginationContainer) return;

    const prevBtn = paginationContainer.querySelector("#prev-btn");
    const nextBtn = paginationContainer.querySelector("#next-btn");
    const pageInfo = paginationContainer.querySelector("#page-info");

    if (prevBtn) {
      prevBtn.disabled = page <= 1 || loading;
      prevBtn.style.opacity = (page <= 1 || loading) ? "0.3" : "1";
      prevBtn.style.cursor = (page <= 1 || loading) ? "not-allowed" : "pointer";
    }

    if (nextBtn) {
      nextBtn.disabled = page >= totalPages || loading;
      nextBtn.style.opacity = (page >= totalPages || loading) ? "0.3" : "1";
      nextBtn.style.cursor = (page >= totalPages || loading) ? "not-allowed" : "pointer";
    }

    if (pageInfo) {
      pageInfo.textContent = `第 ${page} / ${totalPages} 页`;
    }
  };

  const loadWorkflows = async (targetPage = page, forceRefresh = false) => {
    if (loading) return;

    const cacheKey = `${targetPage}_${pageSize}`;

    if (!forceRefresh && isCacheValid(cacheKey)) {
      console.log(`💾 使用缓存数据: 第 ${targetPage} 页`);
      const cachedData = getCachedData(cacheKey);
      workflows = cachedData.list || [];
      total = cachedData.total || 0;
      totalPages = Math.ceil(total / pageSize);
      page = targetPage;

      renderWorkflows();
      updateSubtitle();
      updatePagination();
      return;
    }

    loading = true;
    updatePagination();
    console.log(`📡 加载第 ${targetPage} 页工作流...`);

    try {
      const data = await fetchWorkflows(targetPage, pageSize);
      console.log("📦 工作流数据:", data);

      workflows = data.list;
      total = data.total;
      totalPages = Math.ceil(total / pageSize);
      page = targetPage;

      setCachedData(cacheKey, {
        list: workflows,
        total: total
      });

      setWorkflowsData(workflows);

      renderWorkflows();
      updateSubtitle();
      updatePagination();

      console.log(`✅ 加载成功，第 ${page}/${totalPages} 页，共 ${total} 个工作流 (已缓存)`);
    } catch (error) {
      console.error("❌ 加载工作流失败:", error);
      alert("加载失败：" + error.message);
    } finally {
      loading = false;
      updatePagination();
    }
  };

  const header = document.createElement("div");
  header.style.cssText = `
    padding: 16px;
    border-bottom: 1px solid #404040;
    box-sizing: border-box;
    background: #1a1a1a;
  `

  const titleRow = document.createElement("div");
  titleRow.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    box-sizing: border-box;
  `;

  const subtitle = document.createElement("div");
  subtitle.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
    color: #a0a0a0;
    font-size: 13px;
    overflow: hidden;
  `

  const refreshButton = document.createElement("button");
  refreshButton.innerHTML = '<i class="mdi mdi-refresh"></i>';
  refreshButton.style.cssText = `
    background: transparent;
    border: none;
    color: #a0a0a0;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 18px;
    transition: all 0.2s;
    flex-shrink: 0;
  `

  refreshButton.addEventListener("mouseenter", () => {
    refreshButton.style.background = "#2a2a2a";
    refreshButton.style.color = "#ffffff";
  });

  refreshButton.addEventListener("mouseleave", () => {
    refreshButton.style.background = "transparent";
    refreshButton.style.color = "#a0a0a0";
  })

  const subtitleText = document.createElement("span");
  subtitleText.style.cssText = `
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  `;

  const pageSizeSelect = document.createElement("select");
  pageSizeSelect.style.cssText = `
    background: #2a2a2a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    padding: 2px 6px;
    font-size: 12px;
    cursor: pointer;
    outline: none;
    transition: all 0.2s;
  `;

  [20, 50, 100, 200].forEach(size => {
    const option = document.createElement("option");
    option.value = size;
    option.textContent = size;
    if (size === pageSize) {
      option.selected = true;
    }
    pageSizeSelect.appendChild(option);
  });

  pageSizeSelect.addEventListener("change", async (e) => {
    const newPageSize = parseInt(e.target.value);
    if (newPageSize !== pageSize) {
      pageSize = newPageSize;
      localStorage.setItem('workflow_pageSize', pageSize);

      clearCache();

      page = 1;
      await loadWorkflows(1, true);
    }
  });

  pageSizeSelect.addEventListener("mouseenter", () => {
    pageSizeSelect.style.borderColor = "#606060";
  });

  pageSizeSelect.addEventListener("mouseleave", () => {
    pageSizeSelect.style.borderColor = "#404040";
  });

  subtitle.appendChild(subtitleText);
  subtitle.appendChild(pageSizeSelect);

  const updateSubtitle = () => {
    subtitleText.textContent = `共 ${total} 个工作流 · 每页`;
  };

  titleRow.appendChild(subtitle);
  titleRow.appendChild(refreshButton);
  header.appendChild(titleRow);

  const searchContainer = document.createElement("div");
  searchContainer.style.cssText = `
    padding: 12px 16px;
    border-bottom: 1px solid #404040;
    box-sizing: border-box;
    background: #1a1a1a;
  `

  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.placeholder = "搜索工作流名称或 ID...";
  searchInput.style.cssText = `
    width: 100%;
    padding: 8px 12px 8px 36px;
    border: 1px solid #404040;
    border-radius: 6px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
    box-sizing: border-box;
    background: #2a2a2a url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="%23a0a0a0" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>') no-repeat 12px center;
    color: #ffffff;
  `

  searchInput.addEventListener("focus", () => {
    searchInput.style.borderColor = "#606060";
  });

  searchInput.addEventListener("blur", () => {
    searchInput.style.borderColor = "#404040";
  })

  searchInput.addEventListener("input", (e) => {
    searchKeyword = e.target.value.toLowerCase().trim();
    filterWorkflows();
  });

  searchContainer.appendChild(searchInput);

  const paginationContainer = document.createElement("div");
  paginationContainer.id = "pagination-container";
  paginationContainer.style.cssText = `
    padding: 12px 16px;
    border-bottom: 1px solid #404040;
    box-sizing: border-box;
    background: #1a1a1a;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  `

  const prevBtn = createPaginationButton("上一页", "chevron-left", "left");
  prevBtn.id = "prev-btn";
  prevBtn.addEventListener("click", () => {
    if (page > 1 && !loading) {
      loadWorkflows(page - 1);
    }
  });

  const pageInfo = document.createElement("div");
  pageInfo.id = "page-info";
  pageInfo.style.cssText = `
    color: #a0a0a0;
    font-size: 14px;
    flex: 1;
    text-align: center;
  `
  pageInfo.textContent = `第 ${page} / ${totalPages} 页`;

  const nextBtn = createPaginationButton("下一页", "chevron-right", "right");
  nextBtn.id = "next-btn";
  nextBtn.addEventListener("click", () => {
    if (page < totalPages && !loading) {
      loadWorkflows(page + 1);
    }
  });

  paginationContainer.appendChild(prevBtn);
  paginationContainer.appendChild(pageInfo);
  paginationContainer.appendChild(nextBtn);

  const content = document.createElement("div");
  content.style.cssText = `
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 16px;
    box-sizing: border-box;
    background: #1a1a1a;
  `

  const listContainer = document.createElement("div");
  listContainer.id = "workflow-list-container";
  listContainer.style.cssText = `
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    box-sizing: border-box;
  `;

  content.appendChild(listContainer);

  const refreshWorkflows = async () => {
    refreshButton.querySelector("i").style.animation = "spin 1s linear infinite";

    clearCache();

    workflows = [];
    filteredWorkflows = [];
    page = 1;
    total = 0;
    totalPages = 0;
    searchKeyword = "";
    searchInput.value = "";

    await loadWorkflows(1, true);

    refreshButton.querySelector("i").style.animation = "";
  };

  refreshButton.addEventListener("click", refreshWorkflows);

  container.appendChild(header);
  container.appendChild(searchContainer);
  container.appendChild(paginationContainer);
  container.appendChild(content);
  el.appendChild(container);

  loadWorkflows();

  const style = document.createElement("style");
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateY(20px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);
}
