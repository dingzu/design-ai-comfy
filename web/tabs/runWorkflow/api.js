import { processMediaFiles } from "./mediaProcessor.js";
import { callOriginalGraphToPrompt } from "../../utils/graphToPromptHook.js";
import { validateWorkflow, showValidationErrorDialog } from "./validator.js";

export async function submitWorkflow(taskType = 'wanVideo') {
  if (!window.app || !window.app.graphToPromptOrigin) {
    throw new Error("app.graphToPrompt 方法不存在");
  }

  const prompt = await callOriginalGraphToPrompt(window.app);
  console.log("✅ 获取 Prompt 数据成功:", prompt);

  console.log("🔍 步骤 1: 验证工作流配置");
  const validation = validateWorkflow(prompt.output);
  if (!validation.isValid) {
    console.log("❌ 工作流验证失败，中断提交");
    showValidationErrorDialog(validation.errors);
    throw new Error("工作流验证失败");
  }
  console.log("✅ 工作流验证通过");

  console.log("🔄 步骤 2: 开始处理媒体文件...");
  let processedApiJson;
  try {
    processedApiJson = await processMediaFiles(prompt.output);
    console.log("✅ 媒体文件处理完成");
  } catch (error) {
    console.error("❌ 媒体文件处理失败:", error);
    const errorMessage = `媒体文件上传失败

错误详情：${error.message}

可能的原因：
• 图片或视频文件损坏
• 文件格式不支持
• 网络连接问题
• 文件大小超出限制

请检查您的输入文件并重试。`;

    showValidationErrorDialog([{
      type: 'MEDIA_UPLOAD_ERROR',
      message: errorMessage
    }]);
    throw error;
  }

  const inputParams = [];

  for (const [key, value] of Object.entries(processedApiJson)) {
    if (value.class_type === "LoadImage" && value.inputs.image) {
      inputParams.push({
        apiJsonKey: key,
        nodeId: "",
        nodeName: "LoadImage",
        nodeParamName: "image",
        nodeParam: value.inputs.image
      });
    } else if (value.class_type === "LoadVideo" && value.inputs.file) {
      inputParams.push({
        apiJsonKey: key,
        nodeId: "",
        nodeName: "LoadVideo",
        nodeParamName: "file",
        nodeParam: value.inputs.file
      });
    } else if (value.class_type === "VHS_LoadVideo" && value.inputs.video) {
      inputParams.push({
        apiJsonKey: key,
        nodeId: "",
        nodeName: "VHS_LoadVideo",
        nodeParamName: "video",
        nodeParam: value.inputs.video
      });
    } else if (value.class_type === "LoadImage" && value.inputs.video) {
      inputParams.push({
        apiJsonKey: key,
        nodeId: "",
        nodeName: "LoadImage",
        nodeParamName: "image",
        nodeParam: value.inputs.image
      });
    }
  }

  console.log("📋 构建的 inputParams:", inputParams);

  const requestBody = {
    workflowJson: prompt.workflow,
    apiJson: processedApiJson,
    inputParams: inputParams,
    imageInputSourceType: 2,
    imageResultSourceType: 7,
    taskType: taskType,
    bizToken: "comfyUIToken"
  };

  console.log("📡 提交任务请求:", requestBody);

  const response = await fetch(
    "https://design-ai.staging.kuaishou.com/pub/api/workflow/message/imagine/real/comfy",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log("✅ 任务提交成功:", data);

  if (data.code !== 1) {
    throw new Error(data.errorMsg || "任务提交失败");
  }

  const taskId = data.result.workflowMessage.id;

  return {
    taskId: taskId,
    fullTaskId: `30_${taskId}`,
    status: 1,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    imageResults: [],
    textResults: [],
    errorReason: "",
    origin: null,
    workflowJson: prompt.workflow,
    apiJson: processedApiJson
  };
}

export async function fetchTaskStatus(fullTaskId) {
  const response = await fetch(
    "https://design-ai.staging.kuaishou.com/api/test/GetDesignAIResourceListV2",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: fullTaskId,
        source: 30
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();

  if (data.code !== 200 || !data.design_ai_resources || data.design_ai_resources.length === 0) {
    return null;
  }

  const resource = data.design_ai_resources[0];
  const resourceItems = resource.design_ai_resource_items || [];
  const textItems = resource.design_ai_text_resource_items || [];

  return {
    status: resource.status,
    imageResults: resourceItems.map(item => item.image_url_big),
    textResults: textItems.map(item => item.text),
    errorReason: resource.error_reason || "",
    origin: data
  };
}

export async function pollTaskStatus(fullTaskId, onUpdate, maxAttempts = 60, interval = 3000) {
  let attempts = 0;

  const poll = async () => {
    try {
      attempts++;
      console.log(`🔄 轮询任务状态 (${attempts}/${maxAttempts}): ${fullTaskId}`);

      const result = await fetchTaskStatus(fullTaskId);
      console.log("📦 任务详情:", result);

      if (!result) {
        if (attempts < maxAttempts) {
          setTimeout(poll, interval);
        }
        return;
      }

      onUpdate(result);

      if (result.status === 1 && attempts < maxAttempts) {
        setTimeout(poll, interval);
      } else if (result.status === 4) {
        console.log("✅ 任务完成:", fullTaskId);
      } else if (result.status === 0 || result.status === -1) {
        console.log("❌ 任务失败:", fullTaskId);
      }

    } catch (error) {
      console.error("❌ 获取任务状态失败:", error);
      if (attempts < maxAttempts) {
        setTimeout(poll, interval);
      }
    }
  };

  poll();
}
