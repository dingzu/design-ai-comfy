// 动态加载Material Design Icons
export function loadMaterialDesignIcons() {
  // 检查是否已经加载
  if (document.querySelector('link[href*="materialdesignicons"]')) {
    console.log("📦 Material Design Icons already loaded");
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href =
      "https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/css/materialdesignicons.min.css";

    link.onload = () => {
      console.log("✅ Material Design Icons loaded successfully");
      resolve();
    };

    link.onerror = () => {
      console.error("❌ Failed to load Material Design Icons");
      reject(new Error("Failed to load Material Design Icons"));
    };

    document.head.appendChild(link);
  });
}
