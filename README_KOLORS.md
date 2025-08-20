# 可图（Kolors）API 节点说明

本文档介绍三个可图（Kolors）API 节点的使用方法。

## 节点概述

### 1. 可图文生图 (KolorsTextToImage)
通过文本描述生成图像。

**输入参数:**
- `environment`: 万擎网关环境（staging/prod/idc）
- `api_key`: 万擎网关API密钥
- `prompt`: 图像生成描述提示词
- `model_name`: 可图模型名称（kling-v2）
- `timeout`: 总超时时间（秒）
- `poll_interval`: 轮询间隔（秒）

**输出:**
- `images`: 生成的图像tensor
- `response_json`: 完整API响应JSON
- `usage_info`: 使用统计信息

### 2. 可图图生图 (KolorsImageToImage)
基于输入图像和文本描述进行图像编辑。

**输入参数:**
- `environment`: 万擎网关环境（staging/prod/idc）
- `api_key`: 万擎网关API密钥
- `prompt`: 图像编辑描述提示词
- `model_name`: 可图模型名称（kling-v2）
- `timeout`: 总超时时间（秒）
- `poll_interval`: 轮询间隔（秒）
- `image`: 输入图像（可选）
- `image_url`: 图像URL（当未提供输入图像时使用）

**输出:**
- `images`: 编辑后的图像tensor
- `response_json`: 完整API响应JSON
- `usage_info`: 使用统计信息

### 3. 可图扩图 (KolorsExpandImage)
扩展图像的各个方向，创建更大尺寸的图像。

**输入参数:**
- `environment`: 万擎网关环境（staging/prod/idc）
- `api_key`: 万擎网关API密钥
- `prompt`: 扩展图片描述提示词
- `model_name`: 可图模型名称（kling-v2）
- `up_expansion_ratio`: 向上扩展比例（1.0为不扩展）
- `down_expansion_ratio`: 向下扩展比例（1.0为不扩展）
- `left_expansion_ratio`: 向左扩展比例（1.0为不扩展）
- `right_expansion_ratio`: 向右扩展比例（1.0为不扩展）
- `timeout`: 总超时时间（秒）
- `poll_interval`: 轮询间隔（秒）
- `image`: 输入图像（可选）
- `image_url`: 图像URL（当未提供输入图像时使用）

**输出:**
- `images`: 扩展后的图像tensor
- `response_json`: 完整API响应JSON
- `usage_info`: 使用统计信息

## 使用说明

### API密钥获取
请联系 @于淼 获取万擎网关API密钥。

### 环境配置
- `staging`: 测试环境（推荐用于开发测试）
- `prod`: 生产环境
- `idc`: 内部环境

### 异步处理
所有节点都使用异步处理模式：
1. 首先提交任务获得task_id
2. 然后轮询任务状态直到完成
3. 最终下载生成的图像

### 扩图注意事项
- 扩展比例建议不要过大，API限制总扩展不超过原图3倍
- 如果扩展失败，尝试：
  1. 降低扩展比例
  2. 使用较小的原始图像
  3. 分步进行扩展

### 超时设置
- 建议设置较长的超时时间（300秒或更多）
- 图像生成可能需要较长时间，特别是复杂的生成任务

## 错误处理

节点包含详细的错误处理和提示：
- API密钥验证
- 参数合法性检查
- 网络连接错误处理
- 任务状态监控
- 图像下载失败重试

## 示例工作流

1. **文生图工作流**: 
   - 可图文生图 → 输出图像

2. **图生图工作流**: 
   - 加载图像 → 可图图生图 → 输出编辑后图像

3. **扩图工作流**: 
   - 加载图像 → 可图扩图 → 输出扩展后图像

4. **组合工作流**: 
   - 可图文生图 → 可图扩图 → 最终输出 