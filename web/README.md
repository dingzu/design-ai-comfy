# ComfyUI 插件测试环境

## 项目简介

这是一个用于开发和测试 ComfyUI 扩展插件的本地模拟环境。通过模拟 ComfyUI 的核心 API 和插件系统，开发者可以在独立环境中快速开发、调试和测试插件功能。

## 文件结构

```
.
├── index.html          # 测试页面容器
├── app.js              # ComfyUI 插件系统模拟器
├── main.js             # DesignAI 插件主文件
└── package.json        # 项目配置
```

## 核心文件说明

### `index.html` - 测试页面容器
提供可视化测试界面，包含：
- 模拟 ComfyUI 画布区域
- 实时控制台日志输出
- 版本和状态信息显示
- 使用说明面板
- F12 快捷键切换控制台

### `app.js` - ComfyUI 插件系统模拟器
完整模拟 ComfyUI 的插件 API：
- `app.registerExtension()` - 扩展注册
- `app.extensionManager.registerSidebarTab()` - 侧边栏标签页注册
- 扩展生命周期管理（setup 方法）
- 自动创建侧边栏 UI
- 标签页切换和激活逻辑

### `main.js` - DesignAI 插件
实际的 ComfyUI 插件代码：
- 动态加载 Material Design Icons 图标库
- 注册名为 "DesignAI" 的侧边栏标签页
- 提供记事本功能（自动保存到 localStorage）
- 使用自定义图标和 tooltip

## 运行方式

```bash
# 开发模式
npm run dev

# 生产构建
npm run build
```

## 技术栈

- **Vite** - 构建工具
- **Vanilla JavaScript** - 纯 JS，无框架
- **Material Design Icons** - 图标库
- **LocalStorage** - 数据持久化

## 模拟功能

`app.js` 模拟了以下 ComfyUI API：

```javascript
app.registerExtension(extension)
app.extensionManager.registerSidebarTab(config)
app.extensions
app.canvas
app.graph
```

## 插件开发流程

1. 在 `main.js` 中编写插件代码
2. 使用 `app.registerExtension()` 注册插件
3. 在 `setup()` 生命周期中初始化插件
4. 使用 `registerSidebarTab()` 添加侧边栏功能
5. 在浏览器中实时查看效果

## 注意事项

- 这是模拟环境，与真实 ComfyUI 可能存在差异
- 部署到实际 ComfyUI 时需要调整导入路径
- 建议在真实环境中进行最终测试
