import { loadTasks, loadTasksAsync, saveTasks, addTask, updateTask, deleteTask } from "./runWorkflow/storage.js";
import { showErrorDialog, showWarningDialog, showRawDataDialog, createTaskCard, createEmptyState } from "./runWorkflow/components.js";
import { submitWorkflow, pollTaskStatus } from "./runWorkflow/api.js";
import { getTaskTypes } from "./workflowList/state.js";

export function renderRunWorkflow(el) {
  el.innerHTML = "";

  const container = document.createElement("div");
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #1a1a1a;
    overflow: hidden;
  `;

  const TASKS_PER_PAGE = 20;
  let currentPage = 1;

  const header = document.createElement("div");
  header.style.cssText = `
    padding: 16px;
    border-bottom: 1px solid #404040;
    background: #1a1a1a;
  `;

  const taskTypes = getTaskTypes();
  const savedTaskType = localStorage.getItem('selectedTaskType');
  let selectedTaskType = savedTaskType || 'wanVideo';

  const selectContainer = document.createElement("div");
  selectContainer.style.cssText = `
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
  `;

  const labelWrapper = document.createElement("div");
  labelWrapper.style.cssText = `
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
  `;

  const selectLabel = document.createElement("label");
  selectLabel.textContent = "任务类型：";
  selectLabel.style.cssText = `
    color: #a0a0a0;
    font-size: 13px;
  `;

  const helpIcon = document.createElement("span");
  helpIcon.textContent = "?";
  helpIcon.style.cssText = `
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #404040;
    color: #a0a0a0;
    font-size: 12px;
    font-weight: bold;
    cursor: help;
    transition: all 0.2s;
    position: relative;
  `;

  const tooltip = document.createElement("div");
  tooltip.textContent = "智能适配，如不了解，请勿切换";
  tooltip.style.cssText = `
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(8px);
    padding: 8px 12px;
    background: #2a2a2a;
    color: #ffffff;
    font-size: 12px;
    border-radius: 6px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 99999;
  `;

  let hoverTimer = null;

  helpIcon.addEventListener("mouseenter", () => {
    helpIcon.style.background = "#505050";
    helpIcon.style.color = "#ffffff";

    hoverTimer = setTimeout(() => {
      tooltip.style.opacity = "1";
    }, 2000);
  });

  helpIcon.addEventListener("mouseleave", () => {
    helpIcon.style.background = "#404040";
    helpIcon.style.color = "#a0a0a0";

    if (hoverTimer) {
      clearTimeout(hoverTimer);
      hoverTimer = null;
    }
    tooltip.style.opacity = "0";
  });

  helpIcon.appendChild(tooltip);
  labelWrapper.appendChild(selectLabel);
  labelWrapper.appendChild(helpIcon);

  const taskTypeSelect = document.createElement("select");
  taskTypeSelect.style.cssText = `
    flex: 1;
    padding: 8px 12px;
    background: #2a2a2a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #ffffff;
    font-size: 14px;
    cursor: pointer;
    outline: none;
    transition: all 0.2s;
  `;

  const allTypes = ['wanVideo', ...taskTypes.filter(t => t !== 'wanVideo')];

  if (savedTaskType && !allTypes.includes(savedTaskType)) {
    allTypes.push(savedTaskType);
  }

  allTypes.forEach((type, index) => {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = type;
    if (type === selectedTaskType) {
      option.selected = true;
    }
    taskTypeSelect.appendChild(option);
  });

  taskTypeSelect.addEventListener("change", (e) => {
    selectedTaskType = e.target.value;
    console.log("📌 选择任务类型:", selectedTaskType);

    // 显示提示消息
    showToast("智能适配，如不了解，请勿切换");
  });

  taskTypeSelect.addEventListener("mouseenter", () => {
    taskTypeSelect.style.borderColor = "#606060";
  });

  taskTypeSelect.addEventListener("mouseleave", () => {
    taskTypeSelect.style.borderColor = "#404040";
  });

  const showToast = (message) => {
    const toast = document.createElement("div");
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #2a7ae4;
      color: white;
      padding: 12px 20px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      font-size: 14px;
      animation: slideInRight 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = "slideOutRight 0.3s ease-out";
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  };

  window.updateTaskType = (taskType, skipToast = false) => {
    if (taskType) {
      const existingOption = Array.from(taskTypeSelect.options).find(opt => opt.value === taskType);

      if (!existingOption) {
        const newOption = document.createElement("option");
        newOption.value = taskType;
        newOption.textContent = taskType;
        taskTypeSelect.appendChild(newOption);
      }

      taskTypeSelect.value = taskType;
      selectedTaskType = taskType;

      if (!skipToast) {
        showToast(`任务类型已更新为: ${taskType}`);
      }
    }
  };

  selectContainer.appendChild(labelWrapper);
  selectContainer.appendChild(taskTypeSelect);

  const runButton = document.createElement("button");
  runButton.innerHTML = '<i class="mdi mdi-play"></i> 在 DesignAI 运行当前工作流';
  runButton.style.cssText = `
    padding: 10px 16px;
    background: #2a7ae4;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
  `;

  runButton.addEventListener("mouseenter", () => {
    runButton.style.background = "#1e5bb8";
  });

  runButton.addEventListener("mouseleave", () => {
    runButton.style.background = "#2a7ae4";
  });

  header.appendChild(selectContainer);
  header.appendChild(runButton);

  // 延迟显示运行按钮引导
  setTimeout(() => {
    if (window.onboardingManager && window.showRunWorkflowButtonGuide) {
      window.showRunWorkflowButtonGuide(window.onboardingManager, runButton);
    }
  }, 300);

  const taskListContainer = document.createElement("div");
  taskListContainer.style.cssText = `
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    box-sizing: border-box;
  `;

  const renderTaskList = async () => {
    const allTasks = await loadTasksAsync();
    taskListContainer.innerHTML = "";

    if (allTasks.length === 0) {
      taskListContainer.appendChild(createEmptyState());
      return;
    }

    const reversedTasks = [...allTasks].reverse();
    const totalPages = Math.ceil(reversedTasks.length / TASKS_PER_PAGE);
    const startIndex = (currentPage - 1) * TASKS_PER_PAGE;
    const endIndex = startIndex + TASKS_PER_PAGE;
    const tasks = reversedTasks.slice(startIndex, endIndex);

    // 检查是否需要显示引导
    const shouldShowGuide = currentPage === 1 && tasks.length > 0;

    const contentWrapper = document.createElement("div");
    contentWrapper.style.cssText = `
      display: flex;
      flex-direction: column;
      height: 100%;
    `;

    const paginationInfo = document.createElement("div");
    paginationInfo.style.cssText = `
      padding: 12px 0;
      margin-bottom: 16px;
      border-bottom: 1px solid #404040;
      display: flex;
      justify-content: space-between;
      align-items: center;
    `;

    const infoText = document.createElement("div");
    infoText.textContent = `${allTasks.length} 任务,本地存储`;
    infoText.style.cssText = `
      color: #a0a0a0;
      font-size: 13px;
    `;

    const paginationControls = document.createElement("div");
    paginationControls.style.cssText = `
      display: flex;
      align-items: center;
      gap: 12px;
    `;

    const pageInfo = document.createElement("div");
    pageInfo.textContent = `第 ${currentPage} / ${totalPages} 页`;
    pageInfo.style.cssText = `
      color: #e0e0e0;
      font-size: 13px;
    `;

    const prevBtn = document.createElement("button");
    prevBtn.innerHTML = '<i class="mdi mdi-chevron-left"></i>';
    prevBtn.disabled = currentPage === 1;
    prevBtn.style.cssText = `
      padding: 6px 12px;
      background: ${currentPage === 1 ? '#2a2a2a' : '#404040'};
      color: ${currentPage === 1 ? '#606060' : '#fff'};
      border: none;
      border-radius: 4px;
      font-size: 18px;
      cursor: ${currentPage === 1 ? 'not-allowed' : 'pointer'};
      transition: background 0.2s;
      display: flex;
      align-items: center;
    `;

    const nextBtn = document.createElement("button");
    nextBtn.innerHTML = '<i class="mdi mdi-chevron-right"></i>';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.style.cssText = `
      padding: 6px 12px;
      background: ${currentPage === totalPages ? '#2a2a2a' : '#404040'};
      color: ${currentPage === totalPages ? '#606060' : '#fff'};
      border: none;
      border-radius: 4px;
      font-size: 18px;
      cursor: ${currentPage === totalPages ? 'not-allowed' : 'pointer'};
      transition: background 0.2s;
      display: flex;
      align-items: center;
    `;

    if (currentPage > 1) {
      prevBtn.addEventListener("mouseenter", () => {
        prevBtn.style.background = "#505050";
      });
      prevBtn.addEventListener("mouseleave", () => {
        prevBtn.style.background = "#404040";
      });
      prevBtn.addEventListener("click", () => {
        currentPage--;
        renderTaskList();
      });
    }

    if (currentPage < totalPages) {
      nextBtn.addEventListener("mouseenter", () => {
        nextBtn.style.background = "#505050";
      });
      nextBtn.addEventListener("mouseleave", () => {
        nextBtn.style.background = "#404040";
      });
      nextBtn.addEventListener("click", () => {
        currentPage++;
        renderTaskList();
      });
    }

    paginationControls.appendChild(prevBtn);
    paginationControls.appendChild(pageInfo);
    paginationControls.appendChild(nextBtn);

    paginationInfo.appendChild(infoText);
    paginationInfo.appendChild(paginationControls);

    contentWrapper.appendChild(paginationInfo);

    const cardsContainer = document.createElement("div");
    cardsContainer.style.cssText = `
      flex: 1;
      overflow-y: auto;
    `;

    let isFirstTask = true;
    tasks.forEach((task) => {
      const handleDelete = (taskToDelete) => {
        if (confirm(`确定要删除任务 ${taskToDelete.taskId} 吗？`)) {
          deleteTask(taskToDelete.fullTaskId);

          const remainingTasks = loadTasks();
          const totalPages = Math.ceil(remainingTasks.length / TASKS_PER_PAGE);
          if (currentPage > totalPages && totalPages > 0) {
            currentPage = totalPages;
          }

          renderTaskList();
          console.log("🗑️ 删除任务:", taskToDelete.fullTaskId);
        }
      };

      const handleViewRawData = (taskToView) => {
        showRawDataDialog(taskToView);
      };

      const handleRenderToCanvas = (taskToRender) => {
        if (taskToRender.status === 4 && taskToRender.origin) {
          console.log("🎨 手动渲染任务到画布:", taskToRender.fullTaskId);
          try {
            window.DesignAIRemoteRender?.render(taskToRender.origin);
          } catch (error) {
            console.error("❌ 渲染到画布失败:", error);
            alert("渲染到画布失败：" + error.message);
          }
        }
      };

      const handleLoadWorkflow = (taskToLoad) => {
        if (taskToLoad.workflowJson) {
          console.log("🔄 恢复工作流:", taskToLoad.fullTaskId);
          try {
            if (window.app && window.app.loadGraphData) {
              window.app.loadGraphData(taskToLoad.workflowJson);
              console.log("✅ 工作流恢复成功");
            } else {
              throw new Error("app.loadGraphData 方法不存在");
            }
          } catch (error) {
            console.error("❌ 恢复工作流失败:", error);
            alert("恢复工作流失败：" + error.message);
          }
        }
      };

      const taskCard = createTaskCard(task, handleDelete, showErrorDialog, handleViewRawData, handleRenderToCanvas, handleLoadWorkflow);
      cardsContainer.appendChild(taskCard);

      // 为第一个任务的加载工作流按钮添加引导
      if (isFirstTask && shouldShowGuide) {
        isFirstTask = false;
        setTimeout(() => {
          // 查找该卡片中的"加载工作流"按钮
          const loadWorkflowBtn = taskCard.querySelector('button[title="恢复工作流"]');
          if (loadWorkflowBtn && window.onboardingManager && window.showLoadWorkflowGuide) {
            window.showLoadWorkflowGuide(window.onboardingManager, loadWorkflowBtn);
          }
        }, 500);
      }
    });

    contentWrapper.appendChild(cardsContainer);
    taskListContainer.appendChild(contentWrapper);
  };

  const submitTask = async () => {
    try {
      // 检查运行中的任务数量
      const tasks = loadTasks();
      const runningTasks = tasks.filter(t => t.status === 1);

      if (runningTasks.length > 0) {
        const message = `当前有 ${runningTasks.length} 个任务正在运行中。\n\n请先等待当前任务完成，或删除运行中的任务后再提交新任务。`;
        showWarningDialog(message);
        console.log("⏸️ 阻止提交：存在运行中的任务");
        return;
      }

      runButton.disabled = true;
      runButton.style.opacity = "0.5";
      runButton.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i> 提交中...';

      console.log("📤 开始提交任务...");
      console.log("📌 使用任务类型:", selectedTaskType);

      const task = await submitWorkflow(selectedTaskType);

      addTask(task);

      currentPage = 1;

      renderTaskList();

      pollTaskStatus(task.fullTaskId, (result) => {
        const updatedTask = updateTask(task.fullTaskId, result);
        if (updatedTask) {
          renderTaskList();

          if (updatedTask.status === 4 && updatedTask.origin) {
            console.log("✅ 任务完成，自动渲染到画布:", updatedTask.fullTaskId);
            try {
              window.DesignAIRemoteRender?.render(updatedTask.origin);
            } catch (error) {
              console.error("❌ 渲染到画布失败:", error);
            }
          }
        }
      });

    } catch (error) {
      console.error("❌ 提交任务失败:", error);
      alert("提交任务失败：" + error.message);
    } finally {
      runButton.disabled = false;
      runButton.style.opacity = "1";
      runButton.innerHTML = '<i class="mdi mdi-play"></i> 在 DesignAI 运行当前工作流';
    }
  };

  window.triggerDesignAIWorkflow = submitTask;

  runButton.addEventListener("click", submitTask);

  container.appendChild(header);
  container.appendChild(taskListContainer);
  el.appendChild(container);

  // 显示加载提示
  const loadingIndicator = document.createElement("div");
  loadingIndicator.textContent = "加载任务中...";
  loadingIndicator.style.cssText = `
    padding: 20px;
    text-align: center;
    color: #a0a0a0;
  `;
  taskListContainer.appendChild(loadingIndicator);

  // 异步加载任务列表
  (async () => {
    await renderTaskList();

    const tasks = loadTasks();
    tasks.forEach((task) => {
    if (task.status === 1) {
      console.log("🔄 发现进行中的任务，继续轮询:", task.fullTaskId);
      pollTaskStatus(task.fullTaskId, (result) => {
        const updatedTask = updateTask(task.fullTaskId, result);
        if (updatedTask) {
          renderTaskList();

          if (updatedTask.status === 4 && updatedTask.origin) {
            console.log("✅ 任务完成，自动渲染到画布:", updatedTask.fullTaskId);
            try {
              window.DesignAIRemoteRender?.render(updatedTask.origin);
            } catch (error) {
              console.error("❌ 渲染到画布失败:", error);
            }
          }
        }
      });
    }
    });
  })();

  const style = document.createElement("style");
  style.textContent = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .mdi-spin {
      animation: spin 1s linear infinite;
    }
    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  if (!document.getElementById("runWorkflow-animations")) {
    style.id = "runWorkflow-animations";
    document.head.appendChild(style);
  }
}
