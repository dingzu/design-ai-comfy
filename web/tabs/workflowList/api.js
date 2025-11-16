export async function fetchWorkflows(page, pageSize) {
  const response = await fetch(
    "https://design-out.staging.kuaishou.com/api-token/workflow/list",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "poify-token": "random-code",
      },
      body: JSON.stringify({
        page: page,
        pageSize: pageSize,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();

  if (data.code === 1 && data.data) {
    return {
      list: data.data.list || [],
      total: data.data.total || 0
    };
  } else if (data.errorMsg) {
    throw new Error(data.errorMsg);
  }

  throw new Error("Invalid response format");
}

export function loadWorkflowToCanvas(workflow) {
  if (window.app && window.app.loadGraphData) {
    window.app.loadGraphData(workflow.workflowJson);
    return true;
  }
  return false;
}
