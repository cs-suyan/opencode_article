#!/bin/bash
# Build APK using Docker
# Prerequisites: Docker Desktop installed and running

set -e

echo "============================================"
echo "  AI体育新闻热点文章生成器 - APK 构建脚本"
echo "============================================"
echo ""

# Check if API key is configured (format: android.env = LLM_API_KEY=sk-...)
if grep -qE 'android\.env = LLM_API_KEY=sk-' buildozer.spec 2>/dev/null; then
    echo "[OK] API Key 已配置"
else
    echo "[错误] buildozer.spec 中未找到有效的 android.env 配置"
    echo "       请确保格式正确：android.env = LLM_API_KEY=sk-你的Key"
    exit 1
fi

echo ""
echo "开始构建 APK (首次构建可能需要 30-60 分钟)..."
echo ""

docker compose run --rm buildozer

echo ""
echo "✅ 构建完成！"
echo "APK 文件位于: bin/"
echo "请将 APK 传输到手机安装。"
echo ""
