[app]

# (str) Title of your application
title = AI体育新闻热点生成器

# (str) Package name
package.name = articlegenerator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.opencode

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,toml,md

# (list) List of inclusions using glob patterns
source.include_patterns = src/*.py, config.toml

# (list) Source files to exclude
source.exclude_exts = spec,bat,sh
source.exclude_dirs = tests, venv, .venv, __pycache__, .git, .github, output, bin

# (str) Application versioning
version = 1.0.0

# (str) Application entry point
main.py = app_main.py

# (list) Python requirements
requirements = python3,kivy,requests,beautifulsoup4,python-dotenv,toml,plyer

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported Android API level
android.api = 33

# (int) Minimum Android API level
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version
android.ndk = 25b

# (bool) Enable AndroidX (needed for plyer)
android.enable_androidx = True

# (str) Android permissions
android.permissions = INTERNET

# (str) Android extra Java dependencies (for plyer share)
android.gradle_dependencies = androidx.core:core:1.12.0

# (bool) Indicate whether the application should be fullscreen
android.fullscreen = 0

# (list) Android architectures to build for
android.archs = arm64-v8a

# (str) Environment variables to set at app startup
android.env = LLM_API_KEY=sk-qikbtnfrtruaqeibglhfcxjftyrbttrvateiqyeivbcgyxyx

# (str) Supported iOS version
# ios.min_version = 12.0

# (str) iOS CocoaPods version
# ios.cocoapods_version = 1.12.0

[buildozer]

# (int) Log level (0 = debug, 1 = info, 2 = warning, 3 = error, 4 = critical)
log_level = 1

# (str) Path to build artifact storage
# build_dir = ../.buildozer

# (str) Path to build output (APK location)
# bin_dir = ./bin
