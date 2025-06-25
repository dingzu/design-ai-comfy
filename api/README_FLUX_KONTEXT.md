# FLUX.1 Kontext Pro ComfyUI 节点

这是一个用于 ComfyUI 的自定义节点，允许你通过 Black Forest Labs 的 FLUX.1 Kontext Pro API 生成高质量的图像。

## 功能特性

- 🎨 **文本到图像生成**: 使用 FLUX.1 Kontext Pro 模型从文本描述生成图像
- 📐 **多种宽高比支持**: 支持 1:1, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21, 3:2, 2:3, 5:4, 4:5, 7:3, 3:7
- 🎲 **种子控制**: 支持固定种子以获得可重现的结果
- 🛡️ **安全等级控制**: 可调节的内容审核等级 (0-6)
- 📷 **输出格式选择**: 支持 JPEG 和 PNG 格式
- 🔧 **提示增强**: 可选的提示优化功能
- 🔄 **Webhook 支持**: 可选的异步回调通知

## 使用方法

### 1. 获取 API 密钥

首先，你需要从 [Black Forest Labs](https://api.bfl.ai/) 获取 API 密钥：

1. 访问 https://api.bfl.ai/
2. 创建账户或登录
3. 获取你的 API 密钥
4. 确保账户有足够的积分

### 2. 在 ComfyUI 中使用

1. 在 ComfyUI 的节点菜单中找到 `✨✨✨design-ai/api` 分类
2. 添加 `FLUX.1 Kontext Pro` 节点到你的工作流
3. 配置以下参数：

#### 必需参数

- **api_key**: 你的 Black Forest Labs API 密钥
- **prompt**: 描述你想要生成的图像的文本
- **aspect_ratio**: 图像的宽高比 (默认: "1:1")
- **seed**: 随机种子，-1 表示随机 (默认: -1)
- **prompt_upsampling**: 是否启用提示增强 (默认: false)
- **safety_tolerance**: 安全等级，0 最严格，6 最宽松 (默认: 2)
- **output_format**: 输出格式，"jpeg" 或 "png" (默认: "jpeg")

#### 可选参数

- **webhook_url**: 异步回调 URL (可选)
- **webhook_secret**: Webhook 验证密钥 (可选)

### 3. 输出

节点返回三个值：

- **image**: 生成的图像 (IMAGE 类型)
- **success**: 操作是否成功 (BOOLEAN 类型)
- **message**: 状态消息 (STRING 类型)

## 示例提示

以下是一些可以尝试的示例提示：

### 抽象艺术
```
Abstract expressionist painting Pop Art and cubism early 20 century, straight lines and solids, cute cat face without body, warm colors, green, intricate details, hologram floating in space, a vibrant digital illustration, black background, flat color, 2D, strong lines.
```

### 场景描述
```
A cute round rusted robot repairing a classic pickup truck, colorful, futuristic, vibrant glow, van gogh style
```

### 动物主题
```
A small furry elephant pet looks out from a cat house
```

### 复杂场景
```
Close-up of a vintage car hood under heavy rain, droplets cascading down the deep cherry-red paint, windshield blurred with streaks of water, glowing headlights diffused through mist, reflections of crimson neon signage spelling "FLUX" dancing across the wet chrome grille, steam rising from the engine, ambient red light enveloping the scene, moody composition, shallow depth of field, monochromatic red palette, cinematic lighting with glossy textures.
```

## 注意事项

- 🕐 **生成时间**: 图像生成可能需要几秒到几分钟的时间
- 💰 **API 费用**: 每次生成都会消耗你的 API 积分
- 📏 **图像尺寸**: 默认生成 1024x1024 像素的图像，总像素约为 1MP
- ⏱️ **超时设置**: 节点会等待最多 2 分钟来完成生成
- 🔗 **URL 有效期**: 生成的图像 URL 仅在 10 分钟内有效

## 故障排除

### 常见错误

1. **API key is required**: 请确保输入了有效的 API 密钥
2. **Prompt is required**: 请输入描述图像的文本提示
3. **Request failed**: 检查网络连接和 API 密钥是否正确
4. **Generation timed out**: 服务器可能繁忙，请稍后再试

### 调试建议

- 查看 ComfyUI 控制台输出获取详细错误信息
- 确保网络连接正常
- 验证 API 密钥是否有效且有足够积分
- 尝试简化提示文本

## API 文档

更多详细信息请参考官方文档：
- [FLUX.1 Kontext Text-to-Image API](https://docs.bfl.ai/kontext/kontext_text_to_image)
- [Black Forest Labs API 定价](https://api.bfl.ai/pricing)

## 版本信息

- 版本: 1.0.0
- 兼容性: ComfyUI
- API: FLUX.1 Kontext Pro
- 作者: design-ai-comfy 项目 