# 使用说明

## BlackBorderDetector 节点

### 输入参数
- image (IMAGE)：要处理的输入图像。
- threshold (FLOAT)：检测黑边的阈值（默认值：0.1，范围：0.0 到 1.0）。
- expand (INT)：扩展裁剪区域的像素数（默认值：0，范围：-1000 到 1000）。
- expand_after_crop (INT)：裁剪后扩展的像素数（默认值：0，范围：-1000 到 1000）。
- ignore_threshold (INT)：忽略边界检测的阈值（默认值：-1，范围：-1 到 1000）。

### 输出参数

- cropped_image (IMAGE)：边界检测和裁剪后的图像。
- width (INT)：裁剪后图像的宽度。
- height (INT)：裁剪后图像的高度。
- top_border (INT)：检测到的上黑边。
- bottom_border (INT)：检测到的下黑边。
- left_border (INT)：检测到的左黑边。
- right_border (INT)：检测到的右黑边。
- top_border_add (INT)：额外的上边界扩展。
- bottom_border_add (INT)：额外的下边界扩展。
- left_border_add (INT)：额外的左边界扩展。
- right_border_add (INT)：额外的右边界扩展。

## Cropborder 节点

### 输入参数
- image (IMAGE)：要裁剪的输入图像。
- top (INT)：从顶部裁剪的像素数（默认值：0，范围：0 到 1000）。
- bottom (INT)：从底部裁剪的像素数（默认值：0，范围：0 到 1000）。
- left (INT)：从左侧裁剪的像素数（默认值：0，范围：0 到 1000）。
- right (INT)：从右侧裁剪的像素数（默认值：0，范围：0 到 1000）。

### 输出参数
- cropped_image (IMAGE)：裁剪后的图像。
- width (INT)：裁剪后图像的宽度。
- height (INT)：裁剪后图像的高度。

### 功能描述
Cropborder 节点用于对输入图像进行边界裁剪。它允许用户指定要从图像的上、下、左、右四个边缘裁剪的像素数。裁剪操作会确保裁剪值不超过图像边界。裁剪后，节点会返回裁剪后的图像以及新的宽度和高度。

此节点属于 "✨✨✨design-ai" 类别，可用于图像处理和设计相关任务。