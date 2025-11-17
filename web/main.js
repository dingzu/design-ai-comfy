// import { app, isSimulation } from "./app.js";
import { app } from "../../scripts/app.js";
import { loadMaterialDesignIcons } from "./utils/icons.js";
import { initializeDesignAIRemoteRender } from "./utils/designAIRemoteRender.js";
import { OnboardingManager, showFirstTimeOnboarding, showRunWorkflowButtonGuide, showLoadWorkflowGuide } from "./utils/onboarding.js";
import { installGraphToPromptHook } from "./utils/graphToPromptHook.js";

// 将引导管理器设为全局，以便在不同模块间共享
window.onboardingManager = null;
window.showRunWorkflowButtonGuide = showRunWorkflowButtonGuide;
window.showLoadWorkflowGuide = showLoadWorkflowGuide;
import { renderRunWorkflow } from "./tabs/runWorkflow.js";
import { renderWorkflowList } from "./tabs/workflowList.js";
import { renderSettings } from "./tabs/settings.js";
import { getWorkflowsData, setWorkflowsData } from "./tabs/workflowList/state.js";
import { fetchWorkflows } from "./tabs/workflowList/api.js";
import { isCacheValid, getCachedData, setCachedData } from "./tabs/workflowList/cache.js";
import { loadTasksAsync } from "./tabs/runWorkflow/storage.js";

// 设置模拟环境标识到全局
window.isSimulation = false;

// 初始化 DesignAI Remote Render
initializeDesignAIRemoteRender();

// 初始化引导管理器
window.onboardingManager = new OnboardingManager();

// 立即显示首次引导
showFirstTimeOnboarding(window.onboardingManager);

// 注册 ComfyUI 扩展
app.registerExtension({
  name: "design.ai.comfy.sidebar",

  settings: [
    {
      id: "designai.queue_intercept_mode",
      name: "拦截任务运行模式",
      type: "combo",
      defaultValue: "none",
      options: [
        { text: "不作用 (默认)", value: "none" },
        { text: "拦截", value: "intercept" },
        { text: "不拦截", value: "no_intercept" }
      ],
      category: "DesignAI",
      tooltip: "控制 ComfyUI 原始任务运行的拦截行为。不作用：根据弹窗选择；拦截：总是拦截并弹窗；不拦截：总是直接执行原始流程"
    }
  ],

  async setup() {
    console.log("🚀 DesignAI Sidebar Extension loaded successfully!");
    console.log("Extension name:", this.name);

    // 安装 graphToPrompt Hook
    installGraphToPromptHook(app);

    // 加载图标库
    try {
      await loadMaterialDesignIcons();
    } catch (error) {
      console.error("Failed to load icon library:", error);
    }

    // 加载初始任务
    loadTasksAsync().then(() => {
      console.log("✅ 初始任务加载完成");
    }).catch(err => {
      console.error("❌ 初始任务加载失败:", err);
    });

    console.log("💡 Instructions:");
    console.log("   - Check the sidebar on the right for DesignAI tab");
    console.log("   - Click the DesignAI tab to access workflow management");

    // 注册 DesignAI 侧边栏标签页
    app.extensionManager.registerSidebarTab({
      id: "designai",
      icon: "mdi mdi-alpha-d-box",
      title: "DesignAI",
      tooltip: "DesignAI",
      type: "custom",
      render: async (el) => {
        const cacheKey = '1_100';

        if (!isCacheValid(cacheKey)) {
          console.log("📡 首次加载，自动请求工作流列表...");
          try {
            const data = await fetchWorkflows(1, 100);
            setCachedData(cacheKey, {
              list: data.list,
              total: data.total
            });
            setWorkflowsData(data.list);
            console.log("✅ 工作流列表加载成功，共", data.total, "个工作流");
          } catch (error) {
            console.error("❌ 加载工作流列表失败:", error);
          }
        } else {
          const cachedData = getCachedData(cacheKey);
          setWorkflowsData(cachedData.list || []);
          console.log("💾 使用缓存的工作流数据");
        }
        // 创建主容器
        const mainContainer = document.createElement("div");
        mainContainer.style.cssText = `
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 0;
        `;

        // 创建子标签页头部
        const subTabHeader = document.createElement("div");
        subTabHeader.style.cssText = `
          display: flex;
          background: #1a1a1a;
          border-bottom: 1px solid #404040;
          padding: 0;
        `

        // 创建子标签页内容容器
        const subTabContent = document.createElement("div");
        subTabContent.style.cssText = `
          flex: 1;
          overflow-y: auto;
          padding: 0;
        `;

        // 子标签页数据
        const subTabs = [
          { id: "run-workflow", label: "任务", icon: "mdi mdi-play-circle" },
          { id: "workflow-list", label: "工作流", icon: "mdi mdi-format-list-bulleted" },
          { id: "settings", label: "配置", icon: "mdi mdi-cog" }
        ];

        // 创建子标签页按钮
        subTabs.forEach((tab, index) => {
          const tabBtn = document.createElement("button");
          tabBtn.style.cssText = `
            padding: 12px 16px;
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #a0a0a0;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
          `

          const icon = document.createElement("i");
          icon.className = tab.icon;
          icon.style.fontSize = "16px";

          const label = document.createElement("span");
          label.textContent = tab.label;

          tabBtn.appendChild(icon);
          tabBtn.appendChild(label);

          // 切换标签页
          tabBtn.addEventListener("click", async () => {
            // 重置所有按钮样式
            subTabHeader.querySelectorAll("button").forEach(btn => {
              btn.style.color = "#a0a0a0";
              btn.style.borderBottomColor = "transparent";
            });

            // 激活当前按钮
            tabBtn.style.color = "#ffffff";
            tabBtn.style.borderBottomColor = "#ffffff"

            // 切换内容
            if (tab.id === "run-workflow") {
              renderRunWorkflow(subTabContent);
            } else if (tab.id === "workflow-list") {
              renderWorkflowList(subTabContent);
            } else if (tab.id === "settings") {
              renderSettings(subTabContent);
            }
          });

          // 悬停效果
          tabBtn.addEventListener("mouseenter", () => {
            if (tabBtn.style.color !== "rgb(255, 255, 255)") {
              tabBtn.style.color = "#e0e0e0";
            }
          });

          tabBtn.addEventListener("mouseleave", () => {
            if (tabBtn.style.color !== "rgb(255, 255, 255)") {
              tabBtn.style.color = "#a0a0a0";
            }
          })

          subTabHeader.appendChild(tabBtn);

          // 默认激活第一个标签页
          if (index === 0) {
            tabBtn.click();
          }
        });

        mainContainer.appendChild(subTabHeader);
        mainContainer.appendChild(subTabContent);
        el.appendChild(mainContainer);
      },
    });

    console.log("📋 DesignAI sidebar tabs registered");
  },
});
