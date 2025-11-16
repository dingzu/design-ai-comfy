export function initializeDesignAIRemoteRender() {
  window.DesignAIRemoteRender = window.DesignAIRemoteRender || {};

  const style = document.createElement('style');
  style.textContent = `
    @keyframes flash-highlight {
      0% {
        background-color: rgba(100, 200, 255, 0.3);
        transform: scale(1);
      }
      50% {
        background-color: rgba(100, 200, 255, 0.5);
        transform: scale(1.02);
      }
      100% {
        background-color: transparent;
        transform: scale(1);
      }
    }

    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }

    .design-ai-notification {
      position: fixed;
      top: 20px;
      right: 20px;
      min-width: 300px;
      max-width: 400px;
      background: #2a2a2a;
      border: 1px solid #404040;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
      z-index: 10000;
      animation: slideInRight 0.3s ease-out;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .design-ai-notification.closing {
      animation: slideOutRight 0.3s ease-out;
    }

    .design-ai-notification-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .design-ai-notification-title {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
    }

    .design-ai-notification-close {
      background: transparent;
      border: none;
      color: #a0a0a0;
      font-size: 18px;
      cursor: pointer;
      padding: 0;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .design-ai-notification-close:hover {
      color: #ffffff;
    }

    .design-ai-notification-content {
      font-size: 12px;
      color: #d0d0d0;
      line-height: 1.6;
    }

    .design-ai-notification-item {
      margin-bottom: 8px;
      padding: 8px;
      background: #1a1a1a;
      border-radius: 4px;
      border-left: 3px solid #4a9eff;
    }

    .design-ai-notification-node {
      font-weight: 600;
      color: #4a9eff;
      margin-bottom: 4px;
    }

    .design-ai-notification-stats {
      color: #a0a0a0;
      font-size: 11px;
    }
  `;
  document.head.appendChild(style);

  function showMediaPreviewDialog(mediaUrl, isVideo) {
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

    linkBox.appendChild(linkInput);
    linkBox.appendChild(copyBtn);
    linkBox.appendChild(openBtn);

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
  }

  (function(api){
    const previewCache = new Map();

    const options = {
      maxHeight: 280,
      columns: 2
    };

    const NODE_HEIGHTS = {
      text: 400,
      image: 800,
      video: 800
    };

    function setNodeHeight(node, contentType) {
      if (!node.size) node.size = [300, 200];
      const curW = node.size[0];
      const newH = NODE_HEIGHTS[contentType] || 600;

      if (typeof node.setSize === "function") {
        node.setSize([curW, newH]);
      } else {
        node.size[1] = newH;
      }
      node.setDirtyCanvas?.(true, true);
      window.app?.graph?.setDirtyCanvas?.(true, true);
    }

    function safeParse(str) {
      try {
        return JSON.parse(str);
      } catch (e) {
        console.warn("[DesignAIRemoteRender] workflow_extra_info parse failed:", str, e);
        return null;
      }
    }

    function findNodeById(id) {
      const target = Number(id);
      console.log(`[DesignAIRemoteRender] findNodeById: looking for id=${id}, parsed as ${target}`);

      if (!Number.isFinite(target)) {
        console.warn(`[DesignAIRemoteRender] Invalid node id: ${id}`);
        return null;
      }

      const nodes = (window.app?.graph?._nodes) || [];
      console.log(`[DesignAIRemoteRender] Total nodes in graph: ${nodes.length}`);

      const found = nodes.find(n => n && n.id === target);
      if (found) {
        console.log(`[DesignAIRemoteRender] Found node ${target}:`, {
          id: found.id,
          type: found.type,
          comfyClass: found.comfyClass,
          constructorName: found.constructor?.name
        });
      } else {
        console.warn(`[DesignAIRemoteRender] Node ${target} not found in graph`);
        console.log(`[DesignAIRemoteRender] Available node ids:`, nodes.map(n => n.id));
      }

      return found || null;
    }

    function isSupportedOutputNode(node) {
      const t = (node?.type || node?.comfyClass || node?.constructor?.name || "").toLowerCase();
      const isSupported = (
        t.includes("savetextnode") ||
        t.trim() === "image save".toLowerCase() ||
        t.includes("vhs_videocombine") || t.includes("videocombine")
      );

      console.log(`[DesignAIRemoteRender] isSupportedOutputNode for node ${node?.id}:`, {
        type: node?.type,
        comfyClass: node?.comfyClass,
        constructorName: node?.constructor?.name,
        normalizedType: t,
        isSupported
      });

      return isSupported;
    }

    function ensureDomWidget(node) {
      console.log(`[DesignAIRemoteRender] ensureDomWidget for node ${node.id}`);

      if (previewCache.has(node.id)) {
        const cached = previewCache.get(node.id);
        if (cached.container && cached.container.isConnected) {
          console.log(`[DesignAIRemoteRender] Using cached widget for node ${node.id}`);
          return cached;
        } else {
          console.log(`[DesignAIRemoteRender] Cached widget for node ${node.id} is invalid, recreating...`);
          if (node.__design_ai_ro) {
            try { node.__design_ai_ro.disconnect(); } catch {}
            node.__design_ai_ro = null;
          }
          previewCache.delete(node.id);
        }
      }

      console.log(`[DesignAIRemoteRender] Creating new DOM widget for node ${node.id}`);

      try {
        const div = document.createElement("div");
        div.style.display = "flex";
        div.style.flexDirection = "column";
        div.style.gap = "8px";
        div.style.width = "100%";
        div.style.overflow = "auto";
        div.style.boxSizing = "border-box";
        div.style.padding = "6px";
        div.dataset.remotePreviewContainer = "1";
        div.dataset.nodeId = String(node.id);

        const widget = node.addDOMWidget("Design AI Remote Preview", "div", div);
        const container = div;
        console.log(`[DesignAIRemoteRender] Widget created, container:`, container);

        node.resizable = true;
        node.flags = node.flags || {};
        node.flags.collapsed = false;

        requestAnimationFrame(() => increaseNodeHeight(node));

        const entry = { container, widget };
        previewCache.set(node.id, entry);
        return entry;
      } catch (error) {
        console.error(`[DesignAIRemoteRender] Failed to create widget for node ${node.id}:`, error);
        throw error;
      }
    }

    function badge(label) {
      const s = document.createElement("span");
      s.textContent = label || "";
      s.style.fontSize = "11px";
      s.style.padding = "2px 6px";
      s.style.borderRadius = "999px";
      s.style.border = "1px solid var(--border-color,#444)";
      s.style.opacity = "0.8";
      return s;
    }

    function addFlashAnimation(element) {
      element.style.animation = "flash-highlight 0.6s ease-out";
      element.addEventListener("animationend", () => {
        element.style.animation = "";
      }, { once: true });
    }

    function renderTextCard(nodeName, text) {
      const wrap = document.createElement("div");
      wrap.style.border = "1px solid var(--border-color,#444)";
      wrap.style.borderRadius = "8px";
      wrap.style.padding = "8px";
      wrap.style.display = "flex";
      wrap.style.flexDirection = "column";
      wrap.style.gap = "6px";
      wrap.style.width = "100%";
      wrap.style.boxSizing = "border-box";
      addFlashAnimation(wrap);

      const head = document.createElement("div");
      head.style.display = "flex";
      head.style.justifyContent = "space-between";
      head.style.alignItems = "center";
      head.appendChild(badge(nodeName || "Text"));

      const btn = document.createElement("button");
      btn.textContent = "复制";
      btn.style.fontSize = "12px";
      btn.style.padding = "2px 6px";
      btn.style.border = "1px solid var(--border-color,#444)";
      btn.style.background = "transparent";
      btn.style.borderRadius = "6px";
      btn.style.cursor = "pointer";
      btn.onclick = async () => {
        try {
          await navigator.clipboard.writeText(text || "");
          btn.textContent = "已复制";
          setTimeout(() => btn.textContent = "复制", 1000);
        } catch {}
      };
      head.appendChild(btn);

      const body = document.createElement("div");
      body.style.fontSize = "12px";
      body.style.lineHeight = "1.5";
      body.style.whiteSpace = "pre-wrap";
      body.style.wordBreak = "break-word";
      body.style.maxHeight = "500px";
      body.style.overflow = "auto";
      body.textContent = text ?? "";

      wrap.appendChild(head);
      wrap.appendChild(body);
      return wrap;
    }

    function renderImageCard(nodeName, url) {
      const wrap = document.createElement("div");
      wrap.style.border = "1px solid var(--border-color,#444)";
      wrap.style.borderRadius = "8px";
      wrap.style.padding = "6px";
      wrap.style.display = "flex";
      wrap.style.flexDirection = "column";
      wrap.style.gap = "6px";
      wrap.style.width = "100%";
      wrap.style.boxSizing = "border-box";
      addFlashAnimation(wrap);

      const head = document.createElement("div");
      head.style.display = "flex";
      head.style.justifyContent = "space-between";
      head.style.alignItems = "center";
      head.appendChild(badge(nodeName || "Image"));

      const link = document.createElement("a");
      link.textContent = "新标签打开";
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.style.fontSize = "12px";
      link.style.opacity = "0.8";
      head.appendChild(link);

      const img = new Image();
      img.src = url;
      img.loading = "lazy";
      img.style.width = "100%";
      img.style.height = "auto";
      img.style.objectFit = "contain";
      img.style.borderRadius = "6px";
      img.style.cursor = "pointer";
      img.onclick = () => showMediaPreviewDialog(url, false);

      wrap.appendChild(head);
      wrap.appendChild(img);
      return wrap;
    }

    function renderVideoCard(nodeName, url) {
      const wrap = document.createElement("div");
      wrap.style.border = "1px solid var(--border-color,#444)";
      wrap.style.borderRadius = "8px";
      wrap.style.padding = "6px";
      wrap.style.display = "flex";
      wrap.style.flexDirection = "column";
      wrap.style.gap = "6px";
      wrap.style.width = "100%";
      wrap.style.boxSizing = "border-box";
      addFlashAnimation(wrap);

      const head = document.createElement("div");
      head.style.display = "flex";
      head.style.justifyContent = "space-between";
      head.style.alignItems = "center";
      head.appendChild(badge(nodeName || "Video"));

      const link = document.createElement("a");
      link.textContent = "新标签打开";
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.style.fontSize = "12px";
      link.style.opacity = "0.8";
      head.appendChild(link);

      const videoContainer = document.createElement("div");
      videoContainer.style.position = "relative";
      videoContainer.style.cursor = "pointer";
      videoContainer.onclick = () => showMediaPreviewDialog(url, true);

      const video = document.createElement("video");
      video.controls = false;
      video.preload = "metadata";
      video.style.width = "100%";
      video.style.height = "auto";
      video.style.borderRadius = "6px";
      video.style.pointerEvents = "none";
      const source = document.createElement("source");
      source.src = url;
      video.appendChild(source);

      videoContainer.appendChild(video);

      wrap.appendChild(head);
      wrap.appendChild(videoContainer);
      return wrap;
    }

    function buildNodeResourceMap(payload) {
      console.log(`[DesignAIRemoteRender] buildNodeResourceMap called with payload:`, payload);

      const byId = new Map();
      const ensure = (id) => {
        if (!byId.has(id)) byId.set(id, { textItems: [], imageItems: [], videoItems: [] });
        return byId.get(id);
      };

      const groups = (payload?.design_ai_resources) || [];
      console.log(`[DesignAIRemoteRender] Found ${groups.length} resource groups`);

      for (let gi = 0; gi < groups.length; gi++) {
        const g = groups[gi];
        console.log(`[DesignAIRemoteRender] Processing group ${gi}:`, g);

        const textItems = g?.design_ai_text_resource_items || [];
        console.log(`[DesignAIRemoteRender] Group ${gi} has ${textItems.length} text items`);

        for (let ti = 0; ti < textItems.length; ti++) {
          const item = textItems[ti];
          console.log(`[DesignAIRemoteRender] Processing text item ${ti}:`, item);

          const info = safeParse(item?.workflow_extra_info);
          console.log(`[DesignAIRemoteRender] Parsed workflow_extra_info:`, info);

          const id = Number(info?.apiJsonKey);
          if (!Number.isFinite(id)) {
            console.warn(`[DesignAIRemoteRender] Invalid apiJsonKey for text item:`, info?.apiJsonKey);
            continue;
          }

          console.log(`[DesignAIRemoteRender] Adding text item to node ${id}`);
          ensure(id).textItems.push({
            nodeName: info?.apiJsonKey || "",
            text: item?.text ?? ""
          });
        }

        const mediaItems = g?.design_ai_resource_items || [];
        console.log(`[DesignAIRemoteRender] Group ${gi} has ${mediaItems.length} media items`);

        for (let mi = 0; mi < mediaItems.length; mi++) {
          const item = mediaItems[mi];
          console.log(`[DesignAIRemoteRender] Processing media item ${mi}:`, item);

          const info = safeParse(item?.workflow_extra_info);
          console.log(`[DesignAIRemoteRender] Parsed workflow_extra_info:`, info);

          const id = Number(info?.apiJsonKey);
          if (!Number.isFinite(id)) {
            console.warn(`[DesignAIRemoteRender] Invalid apiJsonKey for media item:`, info?.apiJsonKey);
            continue;
          }

          const rtype = Number(info?.type);
          console.log(`[DesignAIRemoteRender] Media item type: ${rtype}`);

          if (rtype === 3) {
            const src = item?.image_url_medium || item?.image_url_big || item?.image_url_small;
            if (src) {
              console.log(`[DesignAIRemoteRender] Adding image to node ${id}:`, src);
              ensure(id).imageItems.push({ nodeName: info?.apiJsonKey || "", url: src });
            }
          } else if (rtype === 4) {
            const v = item?.video_url || item?.mp4_url || item?.url || item?.image_url_medium || item?.image_url_big || item?.image_url_small;
            console.log(`[DesignAIRemoteRender] Looking for video URL, found:`, v);
            if (v) {
              console.log(`[DesignAIRemoteRender] Adding video to node ${id}:`, v);
              ensure(id).videoItems.push({ nodeName: info?.apiJsonKey || "", url: v });
            } else {
              console.warn(`[DesignAIRemoteRender] No video URL found for item:`, item);
            }
          } else if (rtype === 1) {
            const t = item?.text ?? "";
            console.log(`[DesignAIRemoteRender] Adding text from media to node ${id}`);
            ensure(id).textItems.push({ nodeName: info?.apiJsonKey || "", text: t });
          }
        }
      }

      console.log(`[DesignAIRemoteRender] Built resource map:`, Array.from(byId.entries()));
      return byId;
    }

    function renderForNode(node, entry) {
      console.log(`[DesignAIRemoteRender] renderForNode called for node ${node.id}`, entry);

      if (!isSupportedOutputNode(node)) {
        console.warn(`[DesignAIRemoteRender] Node ${node.id} is not a supported output node, skipping`);
        return;
      }

      console.log(`[DesignAIRemoteRender] Node ${node.id} is supported, creating widget`);

      try {
        const { container } = ensureDomWidget(node);
        container.dataset.nodeId = String(node.id);
        const frag = document.createDocumentFragment();

        let contentType = 'text';

        console.log(`[DesignAIRemoteRender] Rendering ${entry.textItems.length} text items`);
        for (const { nodeName, text } of entry.textItems) {
          frag.appendChild(renderTextCard(nodeName, text));
        }

        console.log(`[DesignAIRemoteRender] Rendering ${entry.imageItems.length} image items`);
        if (entry.imageItems.length > 0) {
          contentType = 'image';
        }
        for (const { nodeName, url } of entry.imageItems) {
          frag.appendChild(renderImageCard(nodeName, url));
        }

        console.log(`[DesignAIRemoteRender] Rendering ${entry.videoItems.length} video items`);
        if (entry.videoItems.length > 0) {
          contentType = 'video';
        }
        for (const { nodeName, url } of entry.videoItems) {
          frag.appendChild(renderVideoCard(nodeName, url));
        }

        console.log(`[DesignAIRemoteRender] Replacing container children`);
        while (container.firstChild) {
          container.removeChild(container.firstChild);
        }
        container.appendChild(frag);

        requestAnimationFrame(() => setNodeHeight(node, contentType));

        console.log(`[DesignAIRemoteRender] Setting node canvas dirty`);
        node.setDirtyCanvas(true, true);

        console.log(`[DesignAIRemoteRender] Successfully rendered node ${node.id}`);
      } catch (error) {
        console.error(`[DesignAIRemoteRender] Error rendering node ${node.id}:`, error);
        throw error;
      }
    }

    function showNotification(renderSummary) {
      const notification = document.createElement('div');
      notification.className = 'design-ai-notification';

      const header = document.createElement('div');
      header.className = 'design-ai-notification-header';

      const title = document.createElement('div');
      title.className = 'design-ai-notification-title';
      title.textContent = '内容填充完成';

      const closeBtn = document.createElement('button');
      closeBtn.className = 'design-ai-notification-close';
      closeBtn.textContent = '×';
      closeBtn.onclick = () => {
        notification.classList.add('closing');
        setTimeout(() => notification.remove(), 300);
      };

      header.appendChild(title);
      header.appendChild(closeBtn);

      const content = document.createElement('div');
      content.className = 'design-ai-notification-content';

      for (const item of renderSummary) {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'design-ai-notification-item';

        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'design-ai-notification-node';
        nodeDiv.textContent = `Node ${item.nodeId}`;

        const statsDiv = document.createElement('div');
        statsDiv.className = 'design-ai-notification-stats';
        const parts = [];
        if (item.textCount > 0) parts.push(`${item.textCount} 个文本`);
        if (item.imageCount > 0) parts.push(`${item.imageCount} 张图片`);
        if (item.videoCount > 0) parts.push(`${item.videoCount} 个视频`);
        statsDiv.textContent = parts.join(', ');

        itemDiv.appendChild(nodeDiv);
        itemDiv.appendChild(statsDiv);
        content.appendChild(itemDiv);
      }

      notification.appendChild(header);
      notification.appendChild(content);
      document.body.appendChild(notification);

      setTimeout(() => {
        notification.classList.add('closing');
        setTimeout(() => notification.remove(), 300);
      }, 5000);
    }

    api.render = function(payload) {
      console.log("[DesignAIRemoteRender] ========== render() called ==========");
      console.log("[DesignAIRemoteRender] Payload:", payload);

      if (!payload) {
        console.warn("[DesignAIRemoteRender] render called with empty payload");
        return;
      }

      if (!window.app) {
        console.error("[DesignAIRemoteRender] window.app is not available");
        return;
      }

      if (!window.app.graph) {
        console.error("[DesignAIRemoteRender] window.app.graph is not available");
        return;
      }

      console.log("[DesignAIRemoteRender] Building node resource map...");
      const map = buildNodeResourceMap(payload);

      console.log(`[DesignAIRemoteRender] Found ${map.size} nodes with resources`);

      let successCount = 0;
      let skipCount = 0;
      const renderSummary = [];

      for (const [id, entry] of map.entries()) {
        console.log(`[DesignAIRemoteRender] Processing node ${id}...`);
        const node = findNodeById(id);

        if (!node) {
          console.warn(`[DesignAIRemoteRender] Skipping node ${id} - not found`);
          skipCount++;
          continue;
        }

        try {
          renderForNode(node, entry);
          successCount++;
          renderSummary.push({
            nodeId: id,
            textCount: entry.textItems.length,
            imageCount: entry.imageItems.length,
            videoCount: entry.videoItems.length
          });
        } catch (error) {
          console.error(`[DesignAIRemoteRender] Failed to render node ${id}:`, error);
          skipCount++;
        }
      }

      console.log(`[DesignAIRemoteRender] Render complete: ${successCount} success, ${skipCount} skipped`);
      console.log(`[DesignAIRemoteRender] Setting global canvas dirty...`);

      window.app?.graph?.setDirtyCanvas?.(true, true);

      if (renderSummary.length > 0) {
        showNotification(renderSummary);
      }

      console.log("[DesignAIRemoteRender] ========== render() finished ==========");
    };

    api.clear = function(nodeId) {
      console.log(`[DesignAIRemoteRender] clear() called for node ${nodeId}`);
      const node = findNodeById(nodeId);
      if (!node) {
        console.warn(`[DesignAIRemoteRender] Node ${nodeId} not found for clear()`);
        return;
      }
      const cached = previewCache.get(node.id);
      if (cached?.container) {
        console.log(`[DesignAIRemoteRender] Clearing container for node ${nodeId}`);
        cached.container.replaceChildren();
      } else {
        console.warn(`[DesignAIRemoteRender] No cached container for node ${nodeId}`);
      }
      node.setDirtyCanvas(true, true);
    };

    api.clearAll = function() {
      console.log(`[DesignAIRemoteRender] clearAll() called, clearing ${previewCache.size} cached nodes`);
      previewCache.forEach((cached, id) => {
        if (cached?.container) {
          console.log(`[DesignAIRemoteRender] Clearing node ${id}`);
          cached.container.replaceChildren();
        }
        const n = findNodeById(id);
        if (n) {
          n.setDirtyCanvas(true, true);
        }
      });
      window.app?.graph?.setDirtyCanvas?.(true, true);
      console.log(`[DesignAIRemoteRender] clearAll() finished`);
    };

    api.setOptions = function(opts={}) {
      console.log(`[DesignAIRemoteRender] setOptions() called:`, opts);
      if (typeof opts.maxHeight === "number") {
        console.log(`[DesignAIRemoteRender] Setting maxHeight to ${opts.maxHeight}`);
        options.maxHeight = opts.maxHeight;
      }
      if (typeof opts.columns === "number" && opts.columns >= 1) {
        console.log(`[DesignAIRemoteRender] Setting columns to ${opts.columns}`);
        options.columns = opts.columns;
      }
      previewCache.forEach(({container}, nodeId)=>{
        if (!container) return;
        container.style.gridTemplateColumns = `repeat(${options.columns}, 1fr)`;
        const node = findNodeById(nodeId);
        if (node) {
          requestAnimationFrame(() => increaseNodeHeight(node));
        }
      });
      window.app?.graph?.setDirtyCanvas?.(true, true);
      console.log(`[DesignAIRemoteRender] setOptions() finished`);
    };

    (function hookLoadGraph(){
      if (!window.app?.loadGraphData || window.app.__design_ai_remote_preview_hooked) {
        console.log("[DesignAIRemoteRender] hookLoadGraph: already hooked or app not ready");
        return;
      }
      console.log("[DesignAIRemoteRender] Hooking app.loadGraphData...");
      const orig = window.app.loadGraphData.bind(window.app);
      window.app.loadGraphData = async function(...args){
        console.log("[DesignAIRemoteRender] loadGraphData hook triggered, clearing preview cache");
        try { api.clearAll(); previewCache.clear(); } catch (e) {
          console.error("[DesignAIRemoteRender] Error during clearAll in hook:", e);
        }
        return await orig(...args);
      };
      window.app.__design_ai_remote_preview_hooked = true;
      console.log("[DesignAIRemoteRender] Successfully hooked app.loadGraphData");
    })();

    console.info("[DesignAIRemoteRender] ready");
  })(window.DesignAIRemoteRender);
}
