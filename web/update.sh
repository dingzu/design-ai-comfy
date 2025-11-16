#!/bin/bash

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法: $0 <zip文件路径>"
    echo "示例: $0 /path/to/your/file.zip"
    exit 1
fi

ZIP_PATH="$1"

# 检查zip文件是否存在
if [ ! -f "$ZIP_PATH" ]; then
    echo "错误: 文件 '$ZIP_PATH' 不存在"
    exit 1
fi

# 检查是否为zip文件
if [[ ! "$ZIP_PATH" =~ \.zip$ ]]; then
    echo "错误: '$ZIP_PATH' 不是zip文件"
    exit 1
fi

# 获取zip文件名
ZIP_FILENAME=$(basename "$ZIP_PATH")

echo "开始处理zip文件: $ZIP_PATH"

# 1. 清理当前目录（保留update.sh）
echo "正在清理当前目录..."
find . -maxdepth 1 -type f ! -name "update.sh" ! -name ".*" -delete
find . -maxdepth 1 -type d ! -name "." ! -name ".git" -exec rm -rf {} +

echo "当前目录清理完成"

# 2. 移动zip文件到当前目录
echo "正在移动zip文件到当前目录..."
mv "$ZIP_PATH" "./$ZIP_FILENAME"

if [ $? -ne 0 ]; then
    echo "错误: 移动文件失败"
    exit 1
fi

echo "移动完成: $ZIP_FILENAME"

# 3. 解压文件到当前目录，覆盖重复文件
echo "正在解压文件..."
unzip -o "./$ZIP_FILENAME"

if [ $? -ne 0 ]; then
    echo "错误: 解压文件失败"
    # 清理已移动的zip文件
    rm -f "./$ZIP_FILENAME"
    exit 1
fi

echo "解压完成"

# 4. 将project目录内容移动到当前目录
echo "正在检查project目录..."

if [ -d "./project" ]; then
    echo "发现project目录，正在移动内容到当前目录..."
    
    # 遍历project目录中的所有文件和目录（包括隐藏文件）
    shopt -s dotglob
    for item in ./project/*; do
        if [ -e "$item" ]; then
            item_name=$(basename "$item")
            
            # 如果目标位置已存在同名目录，先删除
            if [ -d "./$item_name" ]; then
                echo "删除已存在的目录: $item_name"
                rm -rf "./$item_name"
            fi
            
            # 如果目标位置已存在同名文件，先删除
            if [ -f "./$item_name" ]; then
                echo "删除已存在的文件: $item_name"
                rm -f "./$item_name"
            fi
            
            # 移动文件或目录
            mv "$item" "./"
            
            if [ $? -eq 0 ]; then
                echo "已移动: $item_name"
            else
                echo "错误: 移动 $item_name 失败"
                exit 1
            fi
        fi
    done
    shopt -u dotglob
    
    echo "project目录内容移动完成"
    
    # 删除project目录（强制删除，包括可能剩余的隐藏文件）
    echo "正在删除project目录..."
    rm -rf ./project
    
    if [ $? -eq 0 ]; then
        echo "project目录已删除"
    else
        echo "警告: 删除project目录失败"
    fi
else
    echo "注意: 未发现project目录，文件可能直接解压到当前目录"
fi

# 5. 删除zip文件
echo "正在删除zip文件..."
rm -f "./$ZIP_FILENAME"

if [ $? -eq 0 ]; then
    echo "zip文件已删除"
    echo "操作完成！"
else
    echo "警告: 删除zip文件失败"
fi