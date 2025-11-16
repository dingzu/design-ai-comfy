export function showToast(message) {
  const toast = document.createElement("div");
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #2a2a2a;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 10000;
    animation: slideIn 0.3s ease;
    min-width: 300px;
    border: 1px solid #404040;
  `

  const icon = document.createElement("div");
  icon.innerHTML = '<i class="mdi mdi-check-circle"></i>';
  icon.style.cssText = `
    color: #4ade80;
    font-size: 24px;
    flex-shrink: 0;
  `

  const content = document.createElement("div");
  content.style.cssText = "flex: 1;";

  const title = document.createElement("div");
  title.textContent = message;
  title.style.cssText = "font-weight: 600; color: #ffffff; margin-bottom: 4px;"

  const desc = document.createElement("div");
  desc.textContent = "工作流已成功加载到画布";
  desc.style.cssText = "font-size: 12px; color: #a0a0a0;"

  content.appendChild(title);
  content.appendChild(desc);

  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = '<i class="mdi mdi-close"></i>';
  closeBtn.style.cssText = `
    background: transparent;
    border: none;
    color: #808080;
    cursor: pointer;
    padding: 0;
    font-size: 20px;
  `
  closeBtn.addEventListener("click", () => toast.remove());

  toast.appendChild(icon);
  toast.appendChild(content);
  toast.appendChild(closeBtn);
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 5000);
}

export function createWorkflowCard(workflow, onLoad) {
  const card = document.createElement("div");
  card.style.cssText = `
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #2a2a2a;
    border: 1px solid #404040;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    animation: slideIn 0.3s ease;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  `

  card.addEventListener("mouseenter", () => {
    card.style.borderColor = "#606060";
    card.style.transform = "translateY(-2px)";
    card.style.boxShadow = "0 4px 12px rgba(255, 255, 255, 0.1)";
  });

  card.addEventListener("mouseleave", () => {
    card.style.borderColor = "#404040";
    card.style.transform = "translateY(0)";
    card.style.boxShadow = "none";
  })

  card.addEventListener("click", () => onLoad(workflow));

  const cover = document.createElement("img");
  cover.src = workflow.coverUrl || "https://via.placeholder.com/96x96?text=No+Image";
  cover.alt = workflow.name;
  cover.loading = "lazy";
  cover.style.cssText = `
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: 6px;
    flex-shrink: 0;
    background: #404040;
    cursor: pointer;
    transition: transform 0.2s;
  `

  cover.addEventListener("click", (e) => {
    e.stopPropagation();
    showImageModal(workflow.coverUrl || "https://via.placeholder.com/96x96?text=No+Image", workflow.name);
  });

  cover.addEventListener("mouseenter", () => {
    cover.style.transform = "scale(1.05)";
  });

  cover.addEventListener("mouseleave", () => {
    cover.style.transform = "scale(1)";
  });

  const info = document.createElement("div");
  info.style.cssText = `
    flex: 1;
    min-width: 0;
    overflow: hidden;
  `;

  const name = document.createElement("div");
  name.textContent = workflow.name;
  name.style.cssText = `
    font-weight: 600;
    color: #ffffff;
    font-size: 14px;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  `

  const description = document.createElement("div");
  description.textContent = workflow.description || "暂无描述";
  description.style.cssText = `
    font-size: 12px;
    color: #a0a0a0;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  `

  const id = document.createElement("div");
  id.textContent = `ID: ${workflow.id}`;
  id.style.cssText = `
    font-size: 11px;
    color: #808080;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  `

  info.appendChild(name);
  info.appendChild(description);
  info.appendChild(id);

  if (workflow.taskType) {
    const taskType = document.createElement("div");
    taskType.textContent = workflow.taskType;
    taskType.style.cssText = `
      display: inline-block;
      color: #2a7ae4;
      background: rgba(42, 122, 228, 0.15);
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 500;
      font-size: 11px;
    `;

    info.appendChild(taskType);
  }

  const loadIcon = document.createElement("div");
  loadIcon.innerHTML = '<i class="mdi mdi-play-circle"></i>';
  loadIcon.style.cssText = `
    color: #a0a0a0;
    font-size: 24px;
    flex-shrink: 0;
    transition: color 0.2s;
  `

  card.addEventListener("mouseenter", () => {
    loadIcon.style.color = "#ffffff";
  });

  card.addEventListener("mouseleave", () => {
    loadIcon.style.color = "#a0a0a0";
  })

  card.appendChild(cover);
  card.appendChild(info);
  card.appendChild(loadIcon);

  return card;
}

export function createEmptyState() {
  const emptyState = document.createElement("div");
  emptyState.style.cssText = `
    text-align: center;
    padding: 40px 20px;
    color: #808080;
  `
  emptyState.innerHTML = `
    <i class="mdi mdi-file-document-outline" style="font-size: 48px; margin-bottom: 16px; display: block;"></i>
    <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">暂无工作流</div>
    <div style="font-size: 14px;">请稍后刷新查看</div>
  `;
  return emptyState;
}

export function showImageModal(imageUrl, title) {
  const modal = document.createElement("div");
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10001;
    animation: fadeIn 0.2s ease;
    padding: 20px;
    box-sizing: border-box;
  `

  const content = document.createElement("div");
  content.style.cssText = `
    position: relative;
    max-width: 90%;
    max-height: 90%;
    display: flex;
    flex-direction: column;
    animation: zoomIn 0.3s ease;
  `

  const header = document.createElement("div");
  header.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #2a2a2a;
    border-radius: 8px 8px 0 0;
  `

  const titleEl = document.createElement("div");
  titleEl.textContent = title;
  titleEl.style.cssText = `
    color: #ffffff;
    font-weight: 600;
    font-size: 16px;
  `

  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = '<i class="mdi mdi-close"></i>';
  closeBtn.style.cssText = `
    background: transparent;
    border: none;
    color: #a0a0a0;
    cursor: pointer;
    padding: 4px;
    font-size: 24px;
    transition: color 0.2s;
  `

  closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.color = "#ffffff";
  });

  closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.color = "#a0a0a0";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.animation = "fadeOut 0.2s ease";
    setTimeout(() => modal.remove(), 200);
  });

  header.appendChild(titleEl);
  header.appendChild(closeBtn);

  const imageContainer = document.createElement("div");
  imageContainer.style.cssText = `
    background: #1a1a1a;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0 0 8px 8px;
    overflow: auto;
    max-height: 80vh;
  `

  const image = document.createElement("img");
  image.src = imageUrl;
  image.alt = title;
  image.style.cssText = `
    max-width: 100%;
    max-height: 80vh;
    object-fit: contain;
    display: block;
  `

  imageContainer.appendChild(image);
  content.appendChild(header);
  content.appendChild(imageContainer);
  modal.appendChild(content);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.animation = "fadeOut 0.2s ease";
      setTimeout(() => modal.remove(), 200);
    }
  });

  document.addEventListener("keydown", function closeOnEscape(e) {
    if (e.key === "Escape") {
      modal.style.animation = "fadeOut 0.2s ease";
      setTimeout(() => modal.remove(), 200);
      document.removeEventListener("keydown", closeOnEscape);
    }
  });

  document.body.appendChild(modal);

  const style = document.createElement("style");
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
    @keyframes zoomIn {
      from {
        transform: scale(0.9);
        opacity: 0;
      }
      to {
        transform: scale(1);
        opacity: 1;
      }
    }
  `;
  if (!document.querySelector('style[data-image-modal]')) {
    style.setAttribute('data-image-modal', 'true');
    document.head.appendChild(style);
  }
}

export function createPaginationButton(text, icon, position = "left") {
  const btn = document.createElement("button");
  btn.innerHTML = position === "left"
    ? `<i class="mdi mdi-${icon}"></i> ${text}`
    : `${text} <i class="mdi mdi-${icon}"></i>`;

  btn.style.cssText = `
    padding: 8px 16px;
    background: #2a2a2a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #ffffff;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 4px;
  `

  btn.addEventListener("mouseenter", () => {
    if (!btn.disabled) {
      btn.style.background = "#404040";
      btn.style.borderColor = "#606060";
    }
  });

  btn.addEventListener("mouseleave", () => {
    btn.style.background = "#2a2a2a";
    btn.style.borderColor = "#404040";
  });

  return btn;
}
