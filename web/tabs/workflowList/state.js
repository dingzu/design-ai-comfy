import { getAllCachedWorkflows } from "./cache.js";

let taskTypes = [];

export function setWorkflowsData(workflows) {
  updateTaskTypes();
}

function updateTaskTypes() {
  const allWorkflows = getAllCachedWorkflows();

  const typeSet = new Set();
  allWorkflows.forEach(workflow => {
    if (workflow.taskType) {
      typeSet.add(workflow.taskType);
    }
  });

  taskTypes = Array.from(typeSet).sort();

  console.log("📊 聚合 taskType 列表（基于所有缓存数据）:", taskTypes);
  console.log("📦 缓存工作流总数:", allWorkflows.length);
}

export function getWorkflowsData() {
  return getAllCachedWorkflows();
}

export function getTaskTypes() {
  return taskTypes;
}

export function getDefaultWorkflow() {
  const allWorkflows = getAllCachedWorkflows();
  return allWorkflows.find(w => w.id === 'defaultWorkflow') || null;
}
