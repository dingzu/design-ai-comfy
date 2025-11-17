export function showRawDataDialog(taskData) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 24px;
    max-width: 800px;
    width: 90%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.2s;
  `;

  const dialogTitle = document.createElement("div");
  dialogTitle.innerHTML = '<i class="mdi mdi-code-json"></i> 任务原始数据';
  dialogTitle.style.cssText = `
    color: #60a5fa;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const jsonContainer = document.createElement("div");
  jsonContainer.style.cssText = `
    flex: 1;
    overflow-y: auto;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 16px;
  `;

  const jsonPre = document.createElement("pre");
  jsonPre.textContent = JSON.stringify(taskData, null, 2);
  jsonPre.style.cssText = `
    color: #e0e0e0;
    font-size: 13px;
    font-family: 'Courier New', monospace;
    line-height: 1.6;
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
  `;

  jsonContainer.appendChild(jsonPre);

  const buttonContainer = document.createElement("div");
  buttonContainer.style.cssText = `
    display: flex;
    gap: 8px;
  `;

  const copyBtn = document.createElement("button");
  copyBtn.innerHTML = '<i class="mdi mdi-content-copy"></i> 复制 JSON';
  copyBtn.style.cssText = `
    flex: 1;
    padding: 10px 24px;
    background: #60a5fa;
    color: #1a1a1a;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  `;

  copyBtn.addEventListener("mouseenter", () => {
    copyBtn.style.background = "#3b82f6";
  });

  copyBtn.addEventListener("mouseleave", () => {
    copyBtn.style.background = "#60a5fa";
  });

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(taskData, null, 2));
      copyBtn.innerHTML = '<i class="mdi mdi-check"></i> 已复制';
      copyBtn.style.background = "#4ade80";
      setTimeout(() => {
        copyBtn.innerHTML = '<i class="mdi mdi-content-copy"></i> 复制 JSON';
        copyBtn.style.background = "#60a5fa";
      }, 2000);
    } catch (err) {
      console.error("复制失败:", err);
    }
  });

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "关闭";
  closeBtn.style.cssText = `
    flex: 1;
    padding: 10px 24px;
    background: #404040;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  `;

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#505050";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "#404040";
  });

  const closeDialog = () => {
    overlay.style.animation = "fadeOut 0.2s";
    dialog.style.animation = "slideOut 0.2s";
    setTimeout(() => overlay.remove(), 200);
  };

  closeBtn.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeDialog();
  });

  buttonContainer.appendChild(copyBtn);
  buttonContainer.appendChild(closeBtn);

  dialog.appendChild(dialogTitle);
  dialog.appendChild(jsonContainer);
  dialog.appendChild(buttonContainer);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  if (!document.getElementById("error-dialog-animations")) {
    const style = document.createElement("style");
    style.id = "error-dialog-animations";
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
      }
      @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(-20px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

export function showTextDetailModal(text) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 24px;
    max-width: 800px;
    width: 90%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.2s;
  `;

  const dialogTitle = document.createElement("div");
  dialogTitle.innerHTML = '<i class="mdi mdi-text"></i> 文本详情';
  dialogTitle.style.cssText = `
    color: #60a5fa;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const textContainer = document.createElement("div");
  textContainer.style.cssText = `
    flex: 1;
    overflow-y: auto;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 16px;
  `;

  const textContent = document.createElement("div");
  textContent.textContent = text;
  textContent.style.cssText = `
    color: #e0e0e0;
    font-size: 15px;
    line-height: 1.8;
    white-space: pre-wrap;
    word-wrap: break-word;
  `;

  textContainer.appendChild(textContent);

  const buttonContainer = document.createElement("div");
  buttonContainer.style.cssText = `
    display: flex;
    gap: 8px;
  `;

  const copyBtn = document.createElement("button");
  copyBtn.innerHTML = '<i class="mdi mdi-content-copy"></i> 复制文本';
  copyBtn.style.cssText = `
    flex: 1;
    padding: 10px 24px;
    background: #60a5fa;
    color: #1a1a1a;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  `;

  copyBtn.addEventListener("mouseenter", () => {
    copyBtn.style.background = "#3b82f6";
  });

  copyBtn.addEventListener("mouseleave", () => {
    copyBtn.style.background = "#60a5fa";
  });

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      copyBtn.innerHTML = '<i class="mdi mdi-check"></i> 已复制';
      copyBtn.style.background = "#4ade80";
      setTimeout(() => {
        copyBtn.innerHTML = '<i class="mdi mdi-content-copy"></i> 复制文本';
        copyBtn.style.background = "#60a5fa";
      }, 2000);
    } catch (err) {
      console.error("复制失败:", err);
    }
  });

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "关闭";
  closeBtn.style.cssText = `
    flex: 1;
    padding: 10px 24px;
    background: #404040;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  `;

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#505050";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "#404040";
  });

  const closeDialog = () => {
    overlay.style.animation = "fadeOut 0.2s";
    dialog.style.animation = "slideOut 0.2s";
    setTimeout(() => overlay.remove(), 200);
  };

  closeBtn.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeDialog();
  });

  buttonContainer.appendChild(copyBtn);
  buttonContainer.appendChild(closeBtn);

  dialog.appendChild(dialogTitle);
  dialog.appendChild(textContainer);
  dialog.appendChild(buttonContainer);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);
}

export function showPossibleFailureReasonsDialog() {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.2s;
  `;

  const dialogTitle = document.createElement("div");
  dialogTitle.innerHTML = '<i class="mdi mdi-help-circle"></i> 可能的失败原因';
  dialogTitle.style.cssText = `
    color: #fbbf24;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const reasonsList = document.createElement("div");
  reasonsList.style.cssText = `
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.8;
    margin-bottom: 20px;
  `;

  const reasons = [
    {
      title: "使用的模型不存在",
      description: "换一个存在的模型。"
    },
    {
      title: "使用的节点不存在",
      description: "找一个功能一样的节点替换。"
    },
    {
      title: "任务类型不匹配工作流",
      description: "确保没有手动切换任务类型。"
    },
    {
      title: "任务队列已满",
      description: "可以稍后重试。"
    },
    {
      title: "其他未知错误",
      description: "请联系 @wangyihan"
    }
  ];

  reasons.forEach((reason, index) => {
    const reasonItem = document.createElement("div");
    reasonItem.style.cssText = `
      background: #1a1a1a;
      border: 1px solid #404040;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 12px;
    `;

    const reasonTitle = document.createElement("div");
    reasonTitle.textContent = `${index + 1}. ${reason.title}`;
    reasonTitle.style.cssText = `
      color: #fbbf24;
      font-weight: 500;
      margin-bottom: 6px;
    `;

    const reasonDesc = document.createElement("div");
    reasonDesc.textContent = reason.description;
    reasonDesc.style.cssText = `
      color: #a0a0a0;
      font-size: 13px;
    `;

    reasonItem.appendChild(reasonTitle);
    reasonItem.appendChild(reasonDesc);
    reasonsList.appendChild(reasonItem);
  });

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "我知道了";
  closeBtn.style.cssText = `
    padding: 10px 24px;
    background: #fbbf24;
    color: #1a1a1a;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  `;

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#f59e0b";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "#fbbf24";
  });

  const closeDialog = () => {
    overlay.style.animation = "fadeOut 0.2s";
    dialog.style.animation = "slideOut 0.2s";
    setTimeout(() => overlay.remove(), 200);
  };

  closeBtn.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeDialog();
  });

  dialog.appendChild(dialogTitle);
  dialog.appendChild(reasonsList);
  dialog.appendChild(closeBtn);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  if (!document.getElementById("error-dialog-animations")) {
    const style = document.createElement("style");
    style.id = "error-dialog-animations";
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
      }
      @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(-20px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

export function showWarningDialog(message) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 24px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.2s;
  `;

  const dialogTitle = document.createElement("div");
  dialogTitle.innerHTML = '<i class="mdi mdi-alert"></i> 提示';
  dialogTitle.style.cssText = `
    color: #fbbf24;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const dialogContent = document.createElement("div");
  dialogContent.textContent = message;
  dialogContent.style.cssText = `
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.8;
    margin-bottom: 20px;
    word-break: break-word;
  `;

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "我知道了";
  closeBtn.style.cssText = `
    padding: 10px 24px;
    background: #fbbf24;
    color: #1a1a1a;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  `;

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#f59e0b";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "#fbbf24";
  });

  const closeDialog = () => {
    overlay.style.animation = "fadeOut 0.2s";
    dialog.style.animation = "slideOut 0.2s";
    setTimeout(() => overlay.remove(), 200);
  };

  closeBtn.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeDialog();
  });

  dialog.appendChild(dialogTitle);
  dialog.appendChild(dialogContent);
  dialog.appendChild(closeBtn);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  if (!document.getElementById("error-dialog-animations")) {
    const style = document.createElement("style");
    style.id = "error-dialog-animations";
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
      }
      @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(-20px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

export function showErrorDialog(errorMessage) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.2s;
  `;

  const dialogTitle = document.createElement("div");
  dialogTitle.innerHTML = '<i class="mdi mdi-alert-circle"></i> 错误详情';
  dialogTitle.style.cssText = `
    color: #f87171;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const dialogContent = document.createElement("div");
  dialogContent.textContent = errorMessage;
  dialogContent.style.cssText = `
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.8;
    margin-bottom: 20px;
    word-break: break-word;
  `;

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "关闭";
  closeBtn.style.cssText = `
    padding: 8px 24px;
    background: #404040;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  `;

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#505050";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "#404040";
  });

  const closeDialog = () => {
    overlay.style.animation = "fadeOut 0.2s";
    dialog.style.animation = "slideOut 0.2s";
    setTimeout(() => overlay.remove(), 200);
  };

  closeBtn.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeDialog();
  });

  dialog.appendChild(dialogTitle);
  dialog.appendChild(dialogContent);
  dialog.appendChild(closeBtn);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  if (!document.getElementById("error-dialog-animations")) {
    const style = document.createElement("style");
    style.id = "error-dialog-animations";
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
      }
      @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(-20px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

export function createTaskCard(task, onDelete, onErrorClick, onViewRawData, onRenderToCanvas, onLoadWorkflow) {
  const card = document.createElement("div");
  card.style.cssText = `
    background: #2a2a2a;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    transition: all 0.2s;
  `;

  card.addEventListener("mouseenter", () => {
    card.style.borderColor = "#606060";
  });

  card.addEventListener("mouseleave", () => {
    card.style.borderColor = "#404040";
  });

  const taskHeader = document.createElement("div");
  taskHeader.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  `;

  const taskId = document.createElement("div");
  taskId.textContent = `任务 ID: ${task.taskId}`;
  taskId.style.cssText = `
    color: #e0e0e0;
    font-size: 14px;
    font-weight: 500;
  `;

  const headerRight = document.createElement("div");
  headerRight.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const statusBadge = document.createElement("div");
  let statusText = "";
  let statusColor = "";

  switch (task.status) {
    case 1:
      statusText = "处理中";
      statusColor = "#fbbf24";
      break;
    case 4:
      statusText = "成功";
      statusColor = "#4ade80";
      break;
    case 0:
    case -1:
      statusText = "失败";
      statusColor = "#f87171";
      break;
    default:
      statusText = "未知";
      statusColor = "#808080";
  }

  statusBadge.textContent = statusText;
  statusBadge.style.cssText = `
    padding: 4px 12px;
    background: ${statusColor}22;
    color: ${statusColor};
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
  `;

  const loadWorkflowBtn = document.createElement("button");
  loadWorkflowBtn.innerHTML = '<i class="mdi mdi-restore"></i><span style="margin-left: 6px;">加载工作流</span>';
  loadWorkflowBtn.title = "恢复工作流";
  loadWorkflowBtn.style.cssText = `
    padding: 6px 12px;
    background: #7c3aed;
    color: #c4b5fd;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  if (task.workflowJson) {
    loadWorkflowBtn.addEventListener("mouseenter", () => {
      loadWorkflowBtn.style.background = "#6d28d9";
    });

    loadWorkflowBtn.addEventListener("mouseleave", () => {
      loadWorkflowBtn.style.background = "#7c3aed";
    });

    loadWorkflowBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      onLoadWorkflow(task);
    });
  } else {
    loadWorkflowBtn.style.opacity = "0.3";
    loadWorkflowBtn.style.cursor = "not-allowed";
    loadWorkflowBtn.title = "无工作流数据";
  }

  const renderToCanvasBtn = document.createElement("button");
  renderToCanvasBtn.innerHTML = '<i class="mdi mdi-brush"></i><span style="margin-left: 6px;">加载结果</span>';
  renderToCanvasBtn.title = "渲染到画布";
  renderToCanvasBtn.style.cssText = `
    padding: 6px 12px;
    background: #065f46;
    color: #34d399;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  if (task.status === 4 && task.origin) {
    renderToCanvasBtn.addEventListener("mouseenter", () => {
      renderToCanvasBtn.style.background = "#047857";
    });

    renderToCanvasBtn.addEventListener("mouseleave", () => {
      renderToCanvasBtn.style.background = "#065f46";
    });

    renderToCanvasBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      onRenderToCanvas(task);
    });
  } else {
    renderToCanvasBtn.style.opacity = "0.3";
    renderToCanvasBtn.style.cursor = "not-allowed";
    renderToCanvasBtn.title = "仅成功任务可渲染";
  }

  const viewRawDataBtn = document.createElement("button");
  viewRawDataBtn.innerHTML = '<i class="mdi mdi-code-json"></i>';
  viewRawDataBtn.title = "查看原始数据";
  viewRawDataBtn.style.cssText = `
    padding: 4px 8px;
    background: #1e3a8a;
    color: #60a5fa;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  viewRawDataBtn.addEventListener("mouseenter", () => {
    viewRawDataBtn.style.background = "#1e40af";
  });

  viewRawDataBtn.addEventListener("mouseleave", () => {
    viewRawDataBtn.style.background = "#1e3a8a";
  });

  viewRawDataBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    onViewRawData(task);
  });

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "删除";
  deleteBtn.style.cssText = `
    padding: 4px 12px;
    background: #7f1d1d;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: background 0.2s;
  `;

  deleteBtn.addEventListener("mouseenter", () => {
    deleteBtn.style.background = "#991b1b";
  });

  deleteBtn.addEventListener("mouseleave", () => {
    deleteBtn.style.background = "#7f1d1d";
  });

  deleteBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    onDelete(task);
  });

  headerRight.appendChild(statusBadge);
  headerRight.appendChild(viewRawDataBtn);
  headerRight.appendChild(deleteBtn);

  taskHeader.appendChild(taskId);
  taskHeader.appendChild(headerRight);

  // 创建"到 DesignAI 上线工作流"按钮
  const publishToDesignAIBtn = document.createElement("button");
  publishToDesignAIBtn.innerHTML = '<i class="mdi mdi-cloud-upload"></i><span style="margin-left: 6px;">到 DesignAI 上线工作流</span>';
  publishToDesignAIBtn.title = "导出工作流并跳转到 DesignAI";
  publishToDesignAIBtn.style.cssText = `
    padding: 6px 12px;
    background: #0369a1;
    color: #7dd3fc;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  if (task.workflowJson && task.status === 4) {
    publishToDesignAIBtn.addEventListener("mouseenter", () => {
      publishToDesignAIBtn.style.background = "#0c4a6e";
    });

    publishToDesignAIBtn.addEventListener("mouseleave", () => {
      publishToDesignAIBtn.style.background = "#0369a1";
    });

    publishToDesignAIBtn.addEventListener("click", (e) => {
      e.stopPropagation();

      try {
        // 获取工作流 JSON 和 API JSON
        const workflowJson = task.workflowJson;
        const apiJson = task.apiJson;

        // 创建下载链接辅助函数
        const downloadJson = (data, filename) => {
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        };

        // 下载工作流 JSON
        downloadJson(workflowJson, `workflow_${task.taskId}.json`);

        // 如果有 API JSON，也下载
        if (apiJson) {
          downloadJson(apiJson, `workflow_api_${task.taskId}.json`);
        }

        // 延迟跳转，确保下载完成
        setTimeout(() => {
          window.open('https://design-ai.staging.kuaishou.com/workflow/477', '_blank');
        }, 500);

        console.log("✅ 工作流导出成功，即将跳转到 DesignAI");
      } catch (error) {
        console.error("❌ 导出工作流失败:", error);
        alert("导出工作流失败：" + error.message);
      }
    });
  } else {
    publishToDesignAIBtn.style.opacity = "0.3";
    publishToDesignAIBtn.style.cursor = "not-allowed";
    publishToDesignAIBtn.title = task.status === 4 ? "无工作流数据" : "仅成功任务可上线";
  }

  // 创建第一行按钮：加载工作流和加载结果
  const firstButtonRow = document.createElement("div");
  firstButtonRow.style.cssText = `
    display: flex;
    gap: 8px;
    margin-top: 8px;
  `;

  loadWorkflowBtn.style.flex = "1";
  renderToCanvasBtn.style.flex = "1";

  firstButtonRow.appendChild(loadWorkflowBtn);
  firstButtonRow.appendChild(renderToCanvasBtn);

  // 创建第二行按钮：到 DesignAI 上线工作流
  const secondButtonRow = document.createElement("div");
  secondButtonRow.style.cssText = `
    display: flex;
    gap: 8px;
    margin-top: 8px;
  `;

  publishToDesignAIBtn.style.width = "100%";

  secondButtonRow.appendChild(publishToDesignAIBtn);

  const taskTime = document.createElement("div");
  taskTime.textContent = `创建时间: ${new Date(task.createdAt).toLocaleString("zh-CN")}`;
  taskTime.style.cssText = `
    color: #a0a0a0;
    font-size: 12px;
    margin-bottom: 12px;
  `;

  card.appendChild(taskHeader);
  card.appendChild(firstButtonRow);
  card.appendChild(secondButtonRow);
  card.appendChild(taskTime);

  if ((task.status === 0 || task.status === -1) && task.errorReason) {
    const possibleReasonsBtn = document.createElement("button");
    possibleReasonsBtn.innerHTML = '<i class="mdi mdi-help-circle"></i> 可能的失败原因';
    possibleReasonsBtn.style.cssText = `
      width: 100%;
      padding: 8px 12px;
      background: #7f1d1d;
      color: #fca5a5;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      margin-bottom: 8px;
    `;

    possibleReasonsBtn.addEventListener("mouseenter", () => {
      possibleReasonsBtn.style.background = "#991b1b";
    });

    possibleReasonsBtn.addEventListener("mouseleave", () => {
      possibleReasonsBtn.style.background = "#7f1d1d";
    });

    possibleReasonsBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      showPossibleFailureReasonsDialog();
    });

    card.appendChild(possibleReasonsBtn);

    const errorBox = document.createElement("div");
    errorBox.style.cssText = `
      background: #7f1d1d22;
      border: 1px solid #7f1d1d;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: background 0.2s;
    `;

    errorBox.addEventListener("mouseenter", () => {
      errorBox.style.background = "#7f1d1d33";
    });

    errorBox.addEventListener("mouseleave", () => {
      errorBox.style.background = "#7f1d1d22";
    });

    errorBox.addEventListener("click", (e) => {
      e.stopPropagation();
      onErrorClick(task.errorReason);
    });

    const errorTitle = document.createElement("div");
    errorTitle.innerHTML = '<i class="mdi mdi-alert-circle"></i> 错误信息';
    errorTitle.style.cssText = `
      color: #f87171;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 8px;
    `;

    const errorText = document.createElement("div");
    errorText.textContent = task.errorReason;
    errorText.style.cssText = `
      color: #fca5a5;
      font-size: 12px;
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    `;

    errorBox.appendChild(errorTitle);
    errorBox.appendChild(errorText);
    card.appendChild(errorBox);
  }

  if (task.textResults && task.textResults.length > 0) {
    const textSection = document.createElement("div");
    textSection.style.cssText = `
      margin-bottom: 12px;
    `;

    const textTitle = document.createElement("div");
    textTitle.textContent = "文本结果:";
    textTitle.style.cssText = `
      color: #e0e0e0;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 8px;
    `;

    textSection.appendChild(textTitle);

    task.textResults.forEach((text) => {
      const textItem = document.createElement("div");
      textItem.textContent = text;
      textItem.style.cssText = `
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.6;
        padding: 12px;
        background: #1a1a1a;
        border-radius: 4px;
        margin-bottom: 4px;
        cursor: pointer;
        transition: background 0.2s;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
      `;

      textItem.addEventListener("mouseenter", () => {
        textItem.style.background = "#252525";
      });

      textItem.addEventListener("mouseleave", () => {
        textItem.style.background = "#1a1a1a";
      });

      textItem.addEventListener("click", (e) => {
        e.stopPropagation();
        showTextDetailModal(text);
      });

      textSection.appendChild(textItem);
    });

    card.appendChild(textSection);
  }

  if (task.imageResults && task.imageResults.length > 0) {
    const imageSection = document.createElement("div");

    const imageTitle = document.createElement("div");
    imageTitle.textContent = `图片结果 (${task.imageResults.length}):`;
    imageTitle.style.cssText = `
      color: #e0e0e0;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 8px;
    `;

    imageSection.appendChild(imageTitle);

    const imageCount = task.imageResults.length;
    let columns;

    if (imageCount === 1) {
      columns = 1;
    } else if (imageCount === 2) {
      columns = 2;
    } else if (imageCount === 3) {
      columns = 3;
    } else if (imageCount === 4) {
      columns = 2;
    } else if (imageCount <= 6) {
      columns = 3;
    } else if (imageCount <= 9) {
      columns = 3;
    } else {
      columns = 4;
    }

    const imageGrid = document.createElement("div");
    imageGrid.style.cssText = `
      display: grid;
      grid-template-columns: repeat(${columns}, 1fr);
      gap: 8px;
    `;

    task.imageResults.forEach((mediaUrl) => {
      const mediaWrapper = document.createElement("div");
      mediaWrapper.style.cssText = `
        position: relative;
        aspect-ratio: 1;
        border-radius: 6px;
        overflow: hidden;
        background: #404040;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
      `;

      mediaWrapper.addEventListener("mouseenter", () => {
        mediaWrapper.style.transform = "scale(1.05)";
        mediaWrapper.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.5)";
      });

      mediaWrapper.addEventListener("mouseleave", () => {
        mediaWrapper.style.transform = "scale(1)";
        mediaWrapper.style.boxShadow = "none";
      });

      const isVideo = isVideoUrl(mediaUrl);

      if (isVideo) {
        const video = document.createElement("video");
        video.src = mediaUrl;
        video.controls = false;
        video.muted = true;
        video.loop = true;
        video.autoplay = true;
        video.playsInline = true;
        video.style.cssText = `
          width: 100%;
          height: 100%;
          object-fit: cover;
        `;

        const playIcon = document.createElement("div");
        playIcon.innerHTML = '<i class="mdi mdi-play-circle"></i>';
        playIcon.style.cssText = `
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 48px;
          color: white;
          opacity: 0.8;
          pointer-events: none;
          text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        `;

        mediaWrapper.appendChild(video);
        mediaWrapper.appendChild(playIcon);
      } else {
        const img = document.createElement("img");
        img.src = mediaUrl;
        img.alt = "Result";
        img.loading = "lazy";
        img.style.cssText = `
          width: 100%;
          height: 100%;
          object-fit: cover;
        `;

        mediaWrapper.appendChild(img);
      }

      mediaWrapper.addEventListener("click", (e) => {
        e.stopPropagation();
        showMediaDialog(mediaUrl);
      });

      imageGrid.appendChild(mediaWrapper);
    });

    imageSection.appendChild(imageGrid);
    card.appendChild(imageSection);
  }

  return card;
}

function isVideoUrl(url) {
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv'];
  const lowerUrl = url.toLowerCase();
  return videoExtensions.some(ext => lowerUrl.includes(ext));
}

export function showMediaDialog(mediaUrl) {
  const isVideo = isVideoUrl(mediaUrl);
  showMediaDialogInternal(mediaUrl, isVideo);
}

export function showImageDialog(imageUrl) {
  showMediaDialogInternal(imageUrl, false);
}

function showMediaDialogInternal(mediaUrl, isVideo) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s;
    padding: 20px;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 24px;
    max-width: 90vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.2s;
  `;

  const dialogTitle = document.createElement("div");
  dialogTitle.innerHTML = isVideo ? '<i class="mdi mdi-video"></i> 视频详情' : '<i class="mdi mdi-image"></i> 图片详情';
  dialogTitle.style.cssText = `
    color: #e0e0e0;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const mediaContainer = document.createElement("div");
  mediaContainer.style.cssText = `
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    overflow: hidden;
    border-radius: 6px;
    background: #1a1a1a;
    min-height: 300px;
  `;

  if (isVideo) {
    const video = document.createElement("video");
    video.src = mediaUrl;
    video.controls = true;
    video.autoplay = true;
    video.loop = true;
    video.style.cssText = `
      max-width: 100%;
      max-height: 60vh;
      object-fit: contain;
    `;
    mediaContainer.appendChild(video);
  } else {
    const img = document.createElement("img");
    img.src = mediaUrl;
    img.alt = "Preview";
    img.style.cssText = `
      max-width: 100%;
      max-height: 60vh;
      object-fit: contain;
    `;
    mediaContainer.appendChild(img);
  }

  const linkSection = document.createElement("div");
  linkSection.style.cssText = `
    margin-bottom: 16px;
  `;

  const linkLabel = document.createElement("div");
  linkLabel.textContent = isVideo ? "视频链接:" : "图片链接:";
  linkLabel.style.cssText = `
    color: #a0a0a0;
    font-size: 13px;
    margin-bottom: 8px;
  `;

  const linkBox = document.createElement("div");
  linkBox.style.cssText = `
    display: flex;
    gap: 8px;
  `;

  const linkInput = document.createElement("input");
  linkInput.type = "text";
  linkInput.value = mediaUrl;
  linkInput.readOnly = true;
  linkInput.style.cssText = `
    flex: 1;
    padding: 8px 12px;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #e0e0e0;
    font-size: 13px;
    font-family: monospace;
  `;

  const copyBtn = document.createElement("button");
  copyBtn.innerHTML = '<i class="mdi mdi-content-copy"></i> 复制';
  copyBtn.style.cssText = `
    padding: 8px 16px;
    background: #404040;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  `;

  copyBtn.addEventListener("mouseenter", () => {
    copyBtn.style.background = "#505050";
  });

  copyBtn.addEventListener("mouseleave", () => {
    copyBtn.style.background = "#404040";
  });

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(mediaUrl);
      copyBtn.innerHTML = '<i class="mdi mdi-check"></i> 已复制';
      copyBtn.style.background = "#4ade80";
      setTimeout(() => {
        copyBtn.innerHTML = '<i class="mdi mdi-content-copy"></i> 复制';
        copyBtn.style.background = "#404040";
      }, 2000);
    } catch (err) {
      console.error("复制失败:", err);
    }
  });

  const openBtn = document.createElement("button");
  openBtn.innerHTML = '<i class="mdi mdi-open-in-new"></i> 新窗口打开';
  openBtn.style.cssText = `
    padding: 8px 16px;
    background: #2a7ae4;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  `;

  openBtn.addEventListener("mouseenter", () => {
    openBtn.style.background = "#1e5bb8";
  });

  openBtn.addEventListener("mouseleave", () => {
    openBtn.style.background = "#2a7ae4";
  });

  openBtn.addEventListener("click", () => {
    window.open(mediaUrl, "_blank");
  });

  const downloadBtn = document.createElement("button");
  downloadBtn.innerHTML = '<i class="mdi mdi-download"></i> 下载';
  downloadBtn.style.cssText = `
    padding: 8px 16px;
    background: #16a34a;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  `;

  downloadBtn.addEventListener("mouseenter", () => {
    downloadBtn.style.background = "#15803d";
  });

  downloadBtn.addEventListener("mouseleave", () => {
    downloadBtn.style.background = "#16a34a";
  });

  downloadBtn.addEventListener("click", async () => {
    try {
      const response = await fetch(mediaUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // 从 URL 中提取文件名，如果无法提取则使用默认名称
      let filename = mediaUrl.split('/').pop();
      if (!filename || !filename.includes('.')) {
        filename = isVideo ? 'video.mp4' : 'image.png';
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      downloadBtn.innerHTML = '<i class="mdi mdi-check"></i> 已下载';
      downloadBtn.style.background = "#4ade80";
      setTimeout(() => {
        downloadBtn.innerHTML = '<i class="mdi mdi-download"></i> 下载';
        downloadBtn.style.background = "#16a34a";
      }, 2000);
    } catch (err) {
      console.error("下载失败:", err);
      downloadBtn.innerHTML = '<i class="mdi mdi-alert"></i> 下载失败';
      downloadBtn.style.background = "#ef4444";
      setTimeout(() => {
        downloadBtn.innerHTML = '<i class="mdi mdi-download"></i> 下载';
        downloadBtn.style.background = "#16a34a";
      }, 2000);
    }
  });

  linkBox.appendChild(linkInput);
  linkBox.appendChild(copyBtn);
  linkBox.appendChild(openBtn);
  linkBox.appendChild(downloadBtn);

  linkSection.appendChild(linkLabel);
  linkSection.appendChild(linkBox);

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "关闭";
  closeBtn.style.cssText = `
    padding: 8px 24px;
    background: #404040;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  `;

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#505050";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "#404040";
  });

  const closeDialog = () => {
    overlay.style.animation = "fadeOut 0.2s";
    dialog.style.animation = "slideOut 0.2s";
    setTimeout(() => overlay.remove(), 200);
  };

  closeBtn.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeDialog();
  });

  dialog.appendChild(dialogTitle);
  dialog.appendChild(mediaContainer);
  dialog.appendChild(linkSection);
  dialog.appendChild(closeBtn);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  if (!document.getElementById("error-dialog-animations")) {
    const style = document.createElement("style");
    style.id = "error-dialog-animations";
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
      }
      @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(-20px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

export function createEmptyState() {
  const emptyState = document.createElement("div");
  emptyState.style.cssText = `
    text-align: center;
    padding: 60px 20px;
    color: #808080;
  `;
  emptyState.innerHTML = `
    <i class="mdi mdi-file-document-outline" style="font-size: 64px; margin-bottom: 16px; display: block; opacity: 0.5;"></i>
    <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">暂无任务</div>
    <div style="font-size: 14px;">点击"在 DesignAI 运行当前工作流"按钮开始执行任务</div>
  `;
  return emptyState;
}
