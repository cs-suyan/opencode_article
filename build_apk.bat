@echo off
REM Build APK using Docker
REM Prerequisites: Docker Desktop installed and running

echo ============================================
echo   AI体育新闻热点文章生成器 - APK 构建脚本
echo ============================================
echo.
echo 检测 API Key 配置...
echo.

findstr /R "android.env = LLM_API_KEY=sk-" buildozer.spec >nul 2>&1
if %errorlevel%==0 (
    echo [OK] API Key 已配置
) else (
    echo [错误] buildozer.spec 中未找到 android.env 配置
    echo        请确保格式正确：android.env = LLM_API_KEY=sk-你的Key
    pause
    exit /b 1
)

echo.
echo 开始构建 APK (首次构建可能需要 30-60 分钟)...
echo.

docker compose run --rm buildozer

echo.
echo APK 构建完成！
echo APK 文件位于: bin/
echo 请将 APK 传输到手机安装。
echo.

pause
