export function validateWorkflow(apiJson) {
  const errors = [];

  console.log("🔍 开始验证工作流...");

  console.log("📋 步骤 1: 检查节点数量");
  const nodeCountCheck = checkNodeCount(apiJson);
  if (!nodeCountCheck.isValid) {
    errors.push({
      type: 'INSUFFICIENT_NODES',
      message: nodeCountCheck.message,
      details: nodeCountCheck.details
    });
  }

  console.log("📋 步骤 2: 检查输出节点");
  const hasOutputNode = checkOutputNodes(apiJson);
  if (!hasOutputNode.isValid) {
    errors.push({
      type: 'NO_OUTPUT_NODE',
      message: hasOutputNode.message,
      details: hasOutputNode.details
    });
  }

  console.log("📋 步骤 3: 检查禁用节点");
  const blockedNodes = checkBlockedNodes(apiJson);
  if (blockedNodes.length > 0) {
    errors.push({
      type: 'BLOCKED_NODE',
      message: '工作流包含禁止使用的节点',
      details: blockedNodes
    });
  }

  if (errors.length > 0) {
    console.log("❌ 工作流验证失败");
    errors.forEach((error, index) => {
      console.log(`   ${index + 1}. ${error.type}: ${error.message}`);
    });
  } else {
    console.log("✅ 工作流验证通过");
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

function checkNodeCount(apiJson) {
  const nodeCount = Object.keys(apiJson).length;

  console.log(`   当前节点数量: ${nodeCount}`);

  if (nodeCount <= 1) {
    console.log(`   ❌ 节点数量不足`);

    const message = `当前工作流只有 ${nodeCount} 个节点，这不是一个有效的工作流。

一个有效的工作流至少需要包含：
  • 输入节点（如加载图片、文本输入等）
  • 处理节点（如图片处理、模型推理等）
  • 输出节点（如保存图片、保存文本等）

请检查：
  1. 确保工作流已正确加载
  2. 确保工作流包含完整的节点链
  3. 确保没有误删除重要节点

请完善工作流后重新提交。`;

    return {
      isValid: false,
      message,
      details: {
        nodeCount,
        minimumRequired: 2
      }
    };
  }

  console.log(`   ✅ 节点数量充足`);
  return {
    isValid: true,
    nodeCount
  };
}

function checkOutputNodes(apiJson) {
  const outputNodeTypes = [
    'SaveImage',
    'Image Save',
    'SaveTextNode',
    'VHS_VideoCombine'
  ];

  console.log(`   检查输出节点类型: ${outputNodeTypes.join(', ')}`);

  const foundOutputNodes = [];

  for (const [nodeId, nodeData] of Object.entries(apiJson)) {
    const classType = nodeData.class_type;

    if (outputNodeTypes.includes(classType)) {
      foundOutputNodes.push({
        nodeId,
        classType
      });
      console.log(`   ✅ 找到输出节点: ${nodeId} (${classType})`);
    }
  }

  if (foundOutputNodes.length === 0) {
    console.log(`   ❌ 未找到任何输出节点`);

    const message = `当前工作流没有输出节点，无法获取结果。

请根据您的工作流类型添加相应的输出节点：

📷 图片输出：
   • SaveImage - 标准图片保存节点
   • Image Save - 图片保存节点（别名）

📝 文本输出：
   • SaveTextNode - 文本保存节点

🎬 视频输出：
   • VHS_VideoCombine - 视频合成输出节点

请添加输出节点后重新提交任务。`;

    return {
      isValid: false,
      message,
      details: {
        supportedNodes: outputNodeTypes,
        foundCount: 0
      }
    };
  }

  console.log(`   ✅ 找到 ${foundOutputNodes.length} 个输出节点`);
  return {
    isValid: true,
    foundNodes: foundOutputNodes
  };
}

function checkBlockedNodes(apiJson) {
  const blockedNodeTypes = [
    'easy blocker',
    'Easy Blocker'
  ];

  console.log(`   检查禁用节点类型: ${blockedNodeTypes.join(', ')}`);

  const foundBlockedNodes = [];

  for (const [nodeId, nodeData] of Object.entries(apiJson)) {
    const classType = nodeData.class_type;

    const isBlocked = blockedNodeTypes.some(blockedType =>
      classType.toLowerCase().includes(blockedType.toLowerCase())
    );

    if (isBlocked) {
      foundBlockedNodes.push({
        nodeId,
        classType
      });
      console.log(`   ❌ 找到禁用节点: ${nodeId} (${classType})`);
    }
  }

  if (foundBlockedNodes.length > 0) {
    console.log(`   ❌ 找到 ${foundBlockedNodes.length} 个禁用节点`);
  } else {
    console.log(`   ✅ 未找到禁用节点`);
  }

  return foundBlockedNodes;
}

export function showValidationErrorDialog(errors) {
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 100000;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.2s ease-out;
  `;

  const dialog = document.createElement('div');
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    animation: slideUp 0.3s ease-out;
  `;

  const header = document.createElement('div');
  header.style.cssText = `
    padding: 20px 24px;
    border-bottom: 1px solid #404040;
    background: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 12px;
  `;

  const iconWrapper = document.createElement('div');
  iconWrapper.style.cssText = `
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff4444 0%, #ff6b6b 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  `;

  const icon = document.createElement('i');
  icon.className = 'mdi mdi-alert-circle';
  icon.style.cssText = `
    font-size: 24px;
    color: #ffffff;
  `;

  iconWrapper.appendChild(icon);

  const titleEl = document.createElement('h2');
  titleEl.textContent = '工作流验证失败';
  titleEl.style.cssText = `
    margin: 0;
    color: #ffffff;
    font-size: 18px;
    font-weight: 600;
  `;

  header.appendChild(iconWrapper);
  header.appendChild(titleEl);

  const content = document.createElement('div');
  content.style.cssText = `
    padding: 24px;
    overflow-y: auto;
    flex: 1;
  `;

  errors.forEach((error, index) => {
    const errorBlock = document.createElement('div');
    errorBlock.style.cssText = `
      margin-bottom: ${index === errors.length - 1 ? '0' : '20px'};
      padding: 16px;
      background: #1a1a1a;
      border-radius: 8px;
      border-left: 4px solid #ff4444;
    `;

    if (error.type === 'MEDIA_UPLOAD_ERROR') {
      const errorTitle = document.createElement('div');
      errorTitle.style.cssText = `
        color: #ff6b6b;
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      `;
      errorTitle.innerHTML = '<i class="mdi mdi-cloud-upload-outline"></i> 媒体文件上传失败';

      const errorMessage = document.createElement('pre');
      errorMessage.textContent = error.message;
      errorMessage.style.cssText = `
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      `;

      errorBlock.appendChild(errorTitle);
      errorBlock.appendChild(errorMessage);
    } else if (error.type === 'NO_OUTPUT_NODE') {
      const errorTitle = document.createElement('div');
      errorTitle.style.cssText = `
        color: #ff6b6b;
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      `;
      errorTitle.innerHTML = '<i class="mdi mdi-alert"></i> 缺少输出节点';

      const errorMessage = document.createElement('pre');
      errorMessage.textContent = error.message;
      errorMessage.style.cssText = `
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      `;

      errorBlock.appendChild(errorTitle);
      errorBlock.appendChild(errorMessage);
    } else if (error.type === 'BLOCKED_NODE') {
      const errorTitle = document.createElement('div');
      errorTitle.style.cssText = `
        color: #ff6b6b;
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      `;
      errorTitle.innerHTML = '<i class="mdi mdi-cancel"></i> 禁止使用的节点';

      const errorMessage = document.createElement('div');
      errorMessage.style.cssText = `
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 12px;
      `;
      errorMessage.textContent = '工作流中包含以下禁止使用的节点，请删除后重新提交：';

      const nodeList = document.createElement('div');
      nodeList.style.cssText = `
        margin-top: 8px;
      `;

      error.details.forEach(node => {
        const nodeItem = document.createElement('div');
        nodeItem.style.cssText = `
          padding: 8px 12px;
          background: #2a2a2a;
          border-radius: 6px;
          margin-bottom: 8px;
          font-family: 'Courier New', monospace;
          font-size: 13px;
          color: #ff8888;
        `;
        nodeItem.innerHTML = `
          <div style="margin-bottom: 4px;"><strong>节点ID:</strong> ${node.nodeId}</div>
          <div><strong>类型:</strong> ${node.classType}</div>
        `;
        nodeList.appendChild(nodeItem);
      });

      const warning = document.createElement('div');
      warning.style.cssText = `
        margin-top: 12px;
        padding: 12px;
        background: rgba(255, 235, 59, 0.1);
        border: 1px solid rgba(255, 235, 59, 0.3);
        border-radius: 6px;
        color: #ffeb3b;
        font-size: 13px;
        line-height: 1.6;
      `;
      warning.innerHTML = '<i class="mdi mdi-information"></i> <strong>原因：</strong>Easy Blocker 节点会导致工作流执行异常，请使用其他替代方案。';

      errorBlock.appendChild(errorTitle);
      errorBlock.appendChild(errorMessage);
      errorBlock.appendChild(nodeList);
      errorBlock.appendChild(warning);
    } else if (error.type === 'INSUFFICIENT_NODES') {
      const errorTitle = document.createElement('div');
      errorTitle.style.cssText = `
        color: #ff6b6b;
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      `;
      errorTitle.innerHTML = '<i class="mdi mdi-alert"></i> 节点数量不足';

      const errorMessage = document.createElement('pre');
      errorMessage.textContent = error.message;
      errorMessage.style.cssText = `
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      `;

      errorBlock.appendChild(errorTitle);
      errorBlock.appendChild(errorMessage);
    }

    content.appendChild(errorBlock);
  });

  const footer = document.createElement('div');
  footer.style.cssText = `
    padding: 20px 24px;
    border-top: 1px solid #404040;
    background: #1a1a1a;
    display: flex;
    justify-content: flex-end;
  `;

  const closeButton = document.createElement('button');
  closeButton.textContent = '我知道了';
  closeButton.style.cssText = `
    padding: 10px 24px;
    background: #2a7ae4;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  `;

  closeButton.addEventListener('mouseenter', () => {
    closeButton.style.background = '#1e5bb8';
  });

  closeButton.addEventListener('mouseleave', () => {
    closeButton.style.background = '#2a7ae4';
  });

  closeButton.addEventListener('click', () => {
    overlay.style.animation = 'fadeOut 0.2s ease-out';
    setTimeout(() => {
      document.body.removeChild(overlay);
    }, 200);
  });

  footer.appendChild(closeButton);

  dialog.appendChild(header);
  dialog.appendChild(content);
  dialog.appendChild(footer);
  overlay.appendChild(dialog);

  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
    @keyframes slideUp {
      from {
        transform: translateY(30px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
  `;

  if (!document.getElementById('validation-error-animations')) {
    style.id = 'validation-error-animations';
    document.head.appendChild(style);
  }

  document.body.appendChild(overlay);
}
