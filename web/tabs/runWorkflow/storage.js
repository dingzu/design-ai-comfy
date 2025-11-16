const MAX_TASKS = 500;
const INITIAL_TASKS_URL = "https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/c890440cb229c41819804aef0.json";

let isLoadingInitialTasks = false;
let initialTasksPromise = null;

async function loadInitialTasks() {
  if (isLoadingInitialTasks && initialTasksPromise) {
    console.log("⏳ 等待现有的任务加载请求完成...");
    return initialTasksPromise;
  }

  isLoadingInitialTasks = true;
  initialTasksPromise = (async () => {
    try {
      console.log("📥 任务列表为空，正在从远程加载初始任务数据...");
      console.log("🔗 请求 URL:", INITIAL_TASKS_URL);

      const response = await fetch(INITIAL_TASKS_URL);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("📦 收到数据:", data);

      if (Array.isArray(data) && data.length > 0) {
        localStorage.setItem("workflow_tasks", JSON.stringify(data));
        console.log(`✅ 成功加载并保存 ${data.length} 个初始任务`);

        // 检查是否是第一次加载初始任务
        const hasAutoLoadedWorkflow = localStorage.getItem('has_auto_loaded_workflow');
        const lastTask = data[data.length - 1];
        if (!hasAutoLoadedWorkflow && lastTask && lastTask.workflowJson) {
          console.log("🔄 首次加载，自动加载最后一个任务的工作流...");

          // 延迟执行，确保界面已经初始化
          setTimeout(() => {
            try {
              if (window.app && window.app.loadGraphData) {
                window.app.loadGraphData(lastTask.workflowJson);
                console.log("✅ 自动加载工作流成功");
                localStorage.setItem('has_auto_loaded_workflow', 'true');
              } else {
                console.warn("⚠️ app.loadGraphData 方法不存在，稍后重试");
              }
            } catch (error) {
              console.error("❌ 自动加载工作流失败:", error);
            }
          }, 500);
        }

        // 触发更新事件
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('workflow_tasks_updated'));
        }

        return data;
      } else if (data && typeof data === 'object' && !Array.isArray(data)) {
        // 如果数据是对象而不是数组，尝试查找任务数组
        console.log("📦 数据是对象，尝试查找任务数组...");
        const possibleKeys = ['tasks', 'data', 'items', 'list'];

        for (const key of possibleKeys) {
          if (Array.isArray(data[key]) && data[key].length > 0) {
            localStorage.setItem("workflow_tasks", JSON.stringify(data[key]));
            console.log(`✅ 成功从 "${key}" 字段加载并保存 ${data[key].length} 个初始任务`);

            // 检查是否是第一次加载初始任务
            const hasAutoLoadedWorkflow = localStorage.getItem('has_auto_loaded_workflow');
            const lastTask = data[key][data[key].length - 1];
            if (!hasAutoLoadedWorkflow && lastTask && lastTask.workflowJson) {
              console.log("🔄 首次加载，自动加载最后一个任务的工作流...");

              // 延迟执行，确保界面已经初始化
              setTimeout(() => {
                try {
                  if (window.app && window.app.loadGraphData) {
                    window.app.loadGraphData(lastTask.workflowJson);
                    console.log("✅ 自动加载工作流成功");
                    localStorage.setItem('has_auto_loaded_workflow', 'true');
                  } else {
                    console.warn("⚠️ app.loadGraphData 方法不存在，稍后重试");
                  }
                } catch (error) {
                  console.error("❌ 自动加载工作流失败:", error);
                }
              }, 500);
            }

            if (typeof window !== 'undefined') {
              window.dispatchEvent(new CustomEvent('workflow_tasks_updated'));
            }

            return data[key];
          }
        }

        console.warn("⚠️ 无法在数据对象中找到任务数组");
        return [];
      } else {
        console.warn("⚠️ 远程数据格式不正确或为空，数据类型:", typeof data, "是否为数组:", Array.isArray(data));
        return [];
      }
    } catch (error) {
      console.error("❌ 加载初始任务失败:", error);
      console.error("错误详情:", error.message, error.stack);
      return [];
    } finally {
      isLoadingInitialTasks = false;
      initialTasksPromise = null;
    }
  })();

  return initialTasksPromise;
}

export function loadTasks() {
  const storedTasks = JSON.parse(localStorage.getItem("workflow_tasks") || "[]");
  return storedTasks;
}

export async function loadTasksAsync() {
  const storedTasks = JSON.parse(localStorage.getItem("workflow_tasks") || "[]");

  if (storedTasks.length === 0) {
    return await loadInitialTasks();
  }

  return storedTasks;
}

export function saveTasks(tasks) {
  if (tasks.length > MAX_TASKS) {
    tasks = tasks.slice(-MAX_TASKS);
  }
  localStorage.setItem("workflow_tasks", JSON.stringify(tasks));
}

export function addTask(task) {
  const tasks = loadTasks();
  tasks.push(task);
  saveTasks(tasks);
}

export function updateTask(fullTaskId, updates) {
  const tasks = loadTasks();
  const taskIndex = tasks.findIndex(t => t.fullTaskId === fullTaskId);

  if (taskIndex !== -1) {
    tasks[taskIndex] = { ...tasks[taskIndex], ...updates, updatedAt: Date.now() };
    saveTasks(tasks);
    return tasks[taskIndex];
  }

  return null;
}

export function deleteTask(fullTaskId) {
  const tasks = loadTasks();
  const filteredTasks = tasks.filter(t => t.fullTaskId !== fullTaskId);
  saveTasks(filteredTasks);
  return filteredTasks;
}
