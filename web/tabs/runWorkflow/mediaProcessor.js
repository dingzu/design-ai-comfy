export async function processMediaFiles(apiJson) {
  console.log("=".repeat(80));
  console.log("🚀 开始处理媒体文件");
  console.log("=".repeat(80));

  console.log("📋 步骤 1: 解析节点，查找媒体节点");
  const mediaNodes = findMediaNodes(apiJson);

  if (mediaNodes.length === 0) {
    console.log("ℹ️ 没有发现需要处理的媒体节点");
    console.log("=".repeat(80));
    return apiJson;
  }

  console.log(`✅ 发现 ${mediaNodes.length} 个媒体节点需要处理`);
  mediaNodes.forEach((node, index) => {
    console.log(`   ${index + 1}. 节点ID: ${node.nodeId}, 类型: ${node.classType}, 字段: ${node.fieldName}, 文件名: ${node.filename}`);
  });
  console.log("");

  const host = getComfyUIHost();
  console.log(`🌐 ComfyUI 主机地址: ${host}`);
  console.log("");

  for (let i = 0; i < mediaNodes.length; i++) {
    const node = mediaNodes[i];
    const { nodeId, classType, fieldName, filename } = node;

    console.log("-".repeat(80));
    console.log(`📦 处理第 ${i + 1}/${mediaNodes.length} 个节点`);
    console.log(`   节点ID: ${nodeId}`);
    console.log(`   节点类型: ${classType}`);
    console.log(`   字段名: ${fieldName}`);
    console.log(`   原始文件名: ${filename}`);

    if (!filename) {
      console.log(`⚠️ 警告: 节点 ${nodeId} 没有文件名，跳过处理`);
      continue;
    }

    try {
      console.log("");
      console.log(`📥 步骤 2.${i + 1}.1: 拼接下载链接`);
      const localUrl = `${host}/api/view?type=input&filename=${encodeURIComponent(filename)}`;
      console.log(`   完整URL: ${localUrl}`);

      console.log(`📥 步骤 2.${i + 1}.2: 开始下载文件`);
      const blob = await downloadFile(localUrl);

      console.log(`📤 步骤 2.${i + 1}.3: 开始上传到后端`);
      const cdnUrl = await uploadToBackend(blob, filename);

      console.log(`🔄 步骤 2.${i + 1}.4: 回填CDN链接到节点`);
      const originalValue = apiJson[nodeId].inputs[fieldName];
      apiJson[nodeId].inputs[fieldName] = cdnUrl;
      console.log(`   原始值: ${originalValue}`);
      console.log(`   新值: ${cdnUrl}`);
      console.log(`   节点路径: apiJson["${nodeId}"].inputs.${fieldName}`);

      console.log(`✅ 节点 ${nodeId} 处理完成`);
    } catch (error) {
      console.error(`❌ 处理节点 ${nodeId} 失败:`, error);
      console.error(`   错误详情: ${error.message}`);
      throw new Error(`处理媒体文件失败 (节点 ${nodeId}): ${error.message}`);
    }
  }

  console.log("-".repeat(80));
  console.log("✅ 所有媒体文件处理完成");
  console.log("=".repeat(80));
  console.log("");

  return apiJson;
}

function findMediaNodes(apiJson) {
  console.log("🔍 开始扫描所有节点...");
  const mediaNodes = [];
  const totalNodes = Object.keys(apiJson).length;
  console.log(`   总共有 ${totalNodes} 个节点需要扫描`);

  let scannedCount = 0;
  for (const [nodeId, nodeData] of Object.entries(apiJson)) {
    scannedCount++;
    const classType = nodeData.class_type;
    const inputs = nodeData.inputs;

    console.log(`   [${scannedCount}/${totalNodes}] 扫描节点 ${nodeId}: class_type = "${classType}"`);

    if (classType === "LoadImage" && inputs.image) {
      console.log(`      ✅ 匹配到 LoadImage 节点`);
      console.log(`         - 字段: inputs.image`);
      console.log(`         - 值: ${inputs.image}`);
      mediaNodes.push({
        nodeId,
        classType,
        fieldName: "image",
        filename: inputs.image
      });
    } else if (classType === "LoadVideo" && inputs.file) {
      console.log(`      ✅ 匹配到 LoadVideo 节点`);
      console.log(`         - 字段: inputs.file`);
      console.log(`         - 值: ${inputs.file}`);
      mediaNodes.push({
        nodeId,
        classType,
        fieldName: "file",
        filename: inputs.file
      });
    } else if (classType === "VHS_LoadVideo" && inputs.video) {
      console.log(`      ✅ 匹配到 VHS_LoadVideo 节点`);
      console.log(`         - 字段: inputs.video`);
      console.log(`         - 值: ${inputs.video}`);
      mediaNodes.push({
        nodeId,
        classType,
        fieldName: "video",
        filename: inputs.video
      });
    }
  }

  console.log(`✅ 节点扫描完成，找到 ${mediaNodes.length} 个媒体节点`);
  console.log("");
  return mediaNodes;
}

function getComfyUIHost() {
  const hostname = window.location.hostname;
  const origin = window.location.origin;
  const pathname = window.location.pathname;
  const href = window.location.href;

  console.log(`🔧 检测当前环境`);
  console.log(`   hostname: ${hostname}`);
  console.log(`   origin: ${origin}`);
  console.log(`   pathname: ${pathname}`);
  console.log(`   href: ${href}`);

  if (hostname === "localhost" || hostname === "127.0.0.1") {
    const host = "http://127.0.0.1:8188";
    console.log(`   ✅ 检测到本地环境，使用: ${host}`);
    return host;
  }

  const pathParts = pathname.split('/').filter(part => part);
  const basePath = pathParts.length > 0 ? '/' + pathParts.join('/') : '';
  const host = origin + basePath;

  console.log(`   路径部分: ${basePath}`);
  console.log(`   ✅ 检测到远程环境，使用: ${host}`);
  return host;
}

async function downloadFile(url) {
  console.log(`   📥 开始下载文件...`);
  console.log(`      URL: ${url}`);

  const startTime = Date.now();
  const response = await fetch(url);
  const fetchTime = Date.now() - startTime;

  console.log(`      HTTP状态码: ${response.status} ${response.statusText}`);
  console.log(`      请求耗时: ${fetchTime}ms`);

  if (!response.ok) {
    console.error(`      ❌ 下载失败: HTTP ${response.status}`);
    throw new Error(`下载文件失败: ${response.status} ${response.statusText}`);
  }

  const contentType = response.headers.get("content-type");
  const contentLength = response.headers.get("content-length");
  console.log(`      Content-Type: ${contentType}`);
  console.log(`      Content-Length: ${contentLength ? `${contentLength} bytes` : "未知"}`);

  const blob = await response.blob();
  const downloadTime = Date.now() - startTime;

  console.log(`      ✅ 下载完成`);
  console.log(`         - 文件大小: ${(blob.size / 1024).toFixed(2)} KB (${blob.size} bytes)`);
  console.log(`         - 文件类型: ${blob.type}`);
  console.log(`         - 总耗时: ${downloadTime}ms`);

  return blob;
}

async function uploadToBackend(blob, filename) {
  console.log(`   📤 开始上传文件到后端...`);
  console.log(`      文件名: ${filename}`);
  console.log(`      文件大小: ${(blob.size / 1024).toFixed(2)} KB`);
  console.log(`      文件类型: ${blob.type}`);

  const formData = new FormData();
  formData.append("inner", "true");
  formData.append("img", blob, filename);

  console.log(`      FormData 内容:`);
  console.log(`         - inner: true`);
  console.log(`         - img: [Blob] ${filename}`);

  const uploadUrl = "https://design-ai.corp.kuaishou.com/api/pub/other/uploadfile";
  console.log(`      上传URL: ${uploadUrl}`);

  const startTime = Date.now();
  const response = await fetch(uploadUrl, {
    method: "POST",
    body: formData
  });
  const uploadTime = Date.now() - startTime;

  console.log(`      HTTP状态码: ${response.status} ${response.statusText}`);
  console.log(`      上传耗时: ${uploadTime}ms`);

  if (!response.ok) {
    console.error(`      ❌ 上传失败: HTTP ${response.status}`);
    throw new Error(`上传失败: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  console.log(`      响应数据:`, data);

  if (data.code !== 1) {
    console.error(`      ❌ 后端返回错误: code=${data.code}, errorMsg=${data.errorMsg}`);
    throw new Error(data.errorMsg || "上传失败");
  }

  console.log(`      ✅ 上传成功`);
  console.log(`         - CDN URL: ${data.cdnUrl}`);
  console.log(`         - 响应码: ${data.code}`);

  return data.cdnUrl;
}
