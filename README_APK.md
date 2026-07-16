# AI体育新闻热点文章生成器 - APK 构建指南

## 简介

将 Python 项目打包为 Android APK，可在手机端安装使用。

## 前置条件

- **Docker Desktop**（[下载地址](https://www.docker.com/products/docker-desktop/)）
- 至少 **10GB** 磁盘空间
- 首次构建需 **30-60 分钟**（下载 SDK/NDK + 编译依赖）

## 构建步骤

### 1. 确认 API Key 配置

API Key 已在 `buildozer.spec` 中通过 `android.env` 配置好，无需修改。

如需更换 Key，编辑 `buildozer.spec` 第 68 行：
```
android.env = LLM_API_KEY=sk-你的新Key
```

### 2. 运行构建

**Windows：**
```bash
双击 build_apk.bat
```
或在终端运行：
```bash
build_apk.bat
```

**macOS / Linux：**
```bash
chmod +x build_apk.sh
./build_apk.sh
```

### 3. 获取 APK

构建完成后，APK 文件位于项目根目录的 `bin/` 文件夹中：

- `articlegenerator-1.0.0-*-debug.apk`

将 APK 传输到手机安装即可。

> **注意：** 由于是 `debug` 构建，安装时会提示"未知来源"或"检测为有害应用"，这是正常的，选择"仍然安装"即可。

## 在手机上使用

1. 打开应用，点击 **"开始生成"** 按钮
2. 等待采集热点、生成文章（首次生成约 30-60 秒）
3. 生成完成后，日志区域会显示保存路径
4. 点击 **"查看文章"** 可查看今日已生成的文章列表
5. 点击 **"分享文章"** 可通过系统分享将文章发送到微信、QQ 等

## 输出文件

生成的文章存储在手机内部存储的应用私有目录中：

```
/data/data/org.opencode.articlegenerator/files/output/YYYY-MM-DD/
```

如需导出文章，可连接电脑使用 Android Debug Bridge (ADB)：

```bash
adb exec-out run-as org.opencode.articlegenerator cat files/output/2026-07-10/文件名.md > 本地路径.md
```

## 常见问题

### 首次构建失败

首次下载 Android SDK/NDK 可能因网络原因中断，重新运行构建脚本即可继续。

### Docker 权限问题

确保 Docker Desktop 已启动，并且你的用户有权限运行 Docker。

### API 调用报错

确认 buildozer.spec 中 `android.env = LLM_API_KEY=...` 的值正确，且该 API Key 有余额。

### 构建速度慢

首次构建需要下载大量工具链，后续构建会利用缓存，速度会快很多。
