let workflowCache = {
  data: null,
  timestamp: 0,
  ttl: 5 * 60 * 1000
};

export function isCacheValid(cacheKey) {
  if (!workflowCache.data || !workflowCache.data[cacheKey]) return false;
  const now = Date.now();
  const cacheAge = now - workflowCache.timestamp;
  return cacheAge < workflowCache.ttl;
}

export function getCachedData(cacheKey) {
  return workflowCache.data?.[cacheKey];
}

export function setCachedData(cacheKey, data) {
  if (!workflowCache.data) {
    workflowCache.data = {};
  }
  workflowCache.data[cacheKey] = data;
  workflowCache.timestamp = Date.now();
}

export function clearCache() {
  workflowCache.data = null;
  workflowCache.timestamp = 0;
}

export function getAllCachedWorkflows() {
  if (!workflowCache.data) return [];

  const allWorkflows = [];
  const seenIds = new Set();

  Object.values(workflowCache.data).forEach(cacheData => {
    if (cacheData && cacheData.list) {
      cacheData.list.forEach(workflow => {
        if (!seenIds.has(workflow.id)) {
          seenIds.add(workflow.id);
          allWorkflows.push(workflow);
        }
      });
    }
  });

  return allWorkflows;
}
