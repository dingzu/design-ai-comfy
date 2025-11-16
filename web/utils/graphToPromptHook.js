let isHookInstalled = false;
const INTERCEPT_DISABLED_KEY = 'designai_intercept_disabled';

function isInterceptDisabled() {
  return localStorage.getItem(INTERCEPT_DISABLED_KEY) === 'true';
}

function setInterceptDisabled(disabled) {
  localStorage.setItem(INTERCEPT_DISABLED_KEY, disabled ? 'true' : 'false');
}

function isCalledFromQueuePrompt(stack) {
  if (!stack) return false;

  return stack.includes('ComfyApp.queuePrompt');
}

function getCallerInfo(stack) {
  if (!stack) return null;

  const lines = stack.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.includes('graphToPrompt') && i + 1 < lines.length) {
      const callerLine = lines[i + 1].trim();

      const atMatch = callerLine.match(/at\s+(.+?)(\s+\(|$)/);
      if (atMatch) {
        const functionName = atMatch[1];

        const locationMatch = callerLine.match(/\((.+?):(\d+):(\d+)\)/);
        if (locationMatch) {
          return {
            function: functionName,
            file: locationMatch[1],
            line: locationMatch[2],
            column: locationMatch[3],
            fullLine: callerLine
          };
        }

        const simpleLocationMatch = callerLine.match(/at\s+(.+?):(\d+):(\d+)/);
        if (simpleLocationMatch) {
          return {
            function: 'anonymous',
            file: simpleLocationMatch[1],
            line: simpleLocationMatch[2],
            column: simpleLocationMatch[3],
            fullLine: callerLine
          };
        }

        return {
          function: functionName,
          fullLine: callerLine
        };
      }
    }
  }

  return null;
}

export function installGraphToPromptHook(app) {
  if (isHookInstalled || !app || !app.graphToPrompt) {
    return;
  }

  app.graphToPromptOrigin = app.graphToPrompt;

  app.graphToPrompt = async function(...args) {
    const error = new Error();
    const stack = error.stack;

    console.log("🔍 graphToPrompt 被调用");
    console.log("📞 调用堆栈:");
    console.log(stack);

    const callerInfo = getCallerInfo(stack);
    if (callerInfo) {
      console.log("📍 调用来源:", callerInfo);
    }

    const fromQueuePrompt = isCalledFromQueuePrompt(stack);

    if (!fromQueuePrompt) {
      console.log("⏭️ 非 queuePrompt 调用，直接执行原始流程");
      return app.graphToPromptOrigin.apply(this, args);
    }

    console.log("🎯 检测到来自 queuePrompt 的调用");

    // 检查全局设置（优先级最高）
    const interceptMode = app.extensionManager?.setting?.get('designai.queue_intercept_mode') || 'none';
    console.log("⚙️ 当前拦截模式:", interceptMode);

    if (interceptMode === 'no_intercept') {
      console.log("⏭️ 全局设置为不拦截，直接执行原始流程");
      return app.graphToPromptOrigin.apply(this, args);
    }

    if (interceptMode === 'intercept') {
      console.log("🛑 全局设置为拦截，显示确认对话框");
      // 继续执行下面的弹窗逻辑
    } else {
      // interceptMode === 'none'，使用原来的禁用检查逻辑
      if (isInterceptDisabled()) {
        console.log("⏭️ 拦截已禁用，直接执行原始流程");
        return app.graphToPromptOrigin.apply(this, args);
      }
    }

    const result = await showDesignAIConfirmDialog();

    if (result === 'designai') {
      console.log("✅ 用户选择使用 DesignAI，触发 DesignAI 运行逻辑");

      if (window.triggerDesignAIWorkflow) {
        try {
          await window.triggerDesignAIWorkflow();
        } catch (error) {
          console.error("❌ DesignAI 运行失败:", error);
        }
      } else {
        console.error("❌ window.triggerDesignAIWorkflow 方法不存在");
      }

      return null;
    } else if (result === 'original') {
      console.log("✅ 用户选择使用原始流程");
      return app.graphToPromptOrigin.apply(this, args);
    } else {
      console.log("❌ 用户取消操作，阻塞流程");
      return null;
    }
  };

  isHookInstalled = true;
  console.log("🔧 graphToPrompt Hook 已安装");
}

function showDesignAIConfirmDialog() {
  return new Promise((resolve) => {
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
      border-radius: 12px;
      padding: 32px;
      max-width: 500px;
      width: 90%;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
      animation: slideIn 0.2s;
    `;

    const title = document.createElement("div");
    title.innerHTML = '<i class="mdi mdi-alpha-d-box"></i> 选择运行方式';
    title.style.cssText = `
      color: #ffffff;
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
    `;

    const message = document.createElement("div");
    message.innerHTML = `
      <div style="margin-bottom: 12px;">检测到工作流运行请求，您希望如何运行？</div>
      <div style="color: #f59e0b; font-size: 13px; display: flex; align-items: center; gap: 6px;">
        <i class="mdi mdi-alert"></i>
        <span>当前 ComfyUI 服务器可能无法运行模型任务</span>
      </div>
    `;
    message.style.cssText = `
      color: #d0d0d0;
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: 24px;
    `;

    const checkboxContainer = document.createElement("div");
    checkboxContainer.style.cssText = `
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      background: #333333;
      border-radius: 6px;
    `;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = "disable-intercept-checkbox";
    checkbox.style.cssText = `
      width: 16px;
      height: 16px;
      cursor: pointer;
      accent-color: #2a7ae4;
    `;

    const checkboxLabel = document.createElement("label");
    checkboxLabel.htmlFor = "disable-intercept-checkbox";
    checkboxLabel.textContent = "不再拦截，以后都使用原始方式运行";
    checkboxLabel.style.cssText = `
      color: #d0d0d0;
      font-size: 13px;
      cursor: pointer;
      user-select: none;
    `;

    checkboxContainer.appendChild(checkbox);
    checkboxContainer.appendChild(checkboxLabel);

    const buttonsContainer = document.createElement("div");
    buttonsContainer.style.cssText = `
      display: flex;
      gap: 12px;
      justify-content: flex-end;
    `;

    const cancelBtn = document.createElement("button");
    cancelBtn.innerHTML = '<i class="mdi mdi-arrow-left"></i> 使用原始方式';
    cancelBtn.style.cssText = `
      padding: 10px 20px;
      background: #404040;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
    `;

    cancelBtn.addEventListener("mouseenter", () => {
      cancelBtn.style.background = "#505050";
    });

    cancelBtn.addEventListener("mouseleave", () => {
      cancelBtn.style.background = "#404040";
    });

    cancelBtn.addEventListener("click", () => {
      if (checkbox.checked) {
        setInterceptDisabled(true);
        console.log("🔓 拦截已禁用，以后将直接使用原始方式");
      }
      closeDialog();
      resolve('original');
    });

    const confirmBtn = document.createElement("button");
    confirmBtn.innerHTML = '<i class="mdi mdi-alpha-d-box"></i> 使用 DesignAI';
    confirmBtn.style.cssText = `
      padding: 10px 20px;
      background: #2a7ae4;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
    `;

    confirmBtn.addEventListener("mouseenter", () => {
      confirmBtn.style.background = "#1e5bb8";
    });

    confirmBtn.addEventListener("mouseleave", () => {
      confirmBtn.style.background = "#2a7ae4";
    });

    confirmBtn.addEventListener("click", () => {
      if (checkbox.checked) {
        setInterceptDisabled(true);
        console.log("🔓 拦截已禁用，以后将直接使用原始方式");
      }
      closeDialog();
      resolve('designai');
    });

    buttonsContainer.appendChild(cancelBtn);
    buttonsContainer.appendChild(confirmBtn);

    dialog.appendChild(title);
    dialog.appendChild(message);
    dialog.appendChild(checkboxContainer);
    dialog.appendChild(buttonsContainer);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    const closeDialog = () => {
      overlay.style.animation = "fadeOut 0.2s";
      dialog.style.animation = "slideOut 0.2s";
      setTimeout(() => overlay.remove(), 200);
    };

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        closeDialog();
        resolve('cancel');
      }
    });

    if (!document.getElementById("designai-dialog-animations")) {
      const style = document.createElement("style");
      style.id = "designai-dialog-animations";
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
  });
}

export function callOriginalGraphToPrompt(app) {
  if (app && app.graphToPromptOrigin) {
    return app.graphToPromptOrigin();
  }
  throw new Error("Original graphToPrompt method not found");
}
