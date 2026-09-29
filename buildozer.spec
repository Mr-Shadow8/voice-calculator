[app]

# ====== 应用基础信息 ======
title = 语音计算器
package.name = voicecalculator
package.domain = org.calc.voice
package.fullname = 语音计算器

# 版本号(源码方式:直接读取 main.py 所在目录)
version = 1.0.0

# ====== 项目源文件 ======
# 入口文件
source.dir = .
# 需要打包进 APK 的文件/目录(空格分隔)
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json

# 排除调试/缓存文件
source.exclude_dirs = tests, bin, __pycache__, .git, .buildozer
source.exclude_patterns = Makefile, README*, *.md, *.spec.bak

# ====== Python 运行时 ======
# 推荐用 Python 3.11,兼容性最佳
requirements = python3,kivy==2.3.0,pyjnius==2.3.0

# 选用 Kivy2 分支(python3 后端)
# 如要启用 Kivy3 / SDL2 调试可改 orientation 等参数
garden_requirements =

# ====== Android 构建配置 ======
# 架构:大多数手机用 arm64-v8a;老设备兼容 armeabi-v7a
android.archs = arm64-v8a, armeabi-v7a

# 最低 SDK / 目标 SDK(默认值即可)
android.api = 31
android.minapi = 21
android.ndk = 25b

# 主屏幕方向:竖屏(计算器是竖屏应用)
orientation = portrait

# 是否全屏(0=不全屏,显示状态栏)
fullscreen = 0

# ====== 权限说明 ======
# Android TTS 是系统服务,本身不需要特殊权限
# 加 CHANGE_* 允许 TTS 安装语音数据(可选)
android.permissions =
android.accept_android_license = True

# ====== APK 签名(默认 debug 签名,可自填 release 签名) ======
# 调试构建用默认 debug keystore 即可
# 如要上架需自己生成 keystore:
#   keytool -genkeypair -v -keystore release.keystore -alias voice-calc -keyalg RSA -keysize 2048 -validity 10000
# 然后取消下面注释:
# android.release_artifact = apk
# android.release_keystore = release.keystore
# android.release_key_alias = voice-calc
# android.release_key_password = YOUR_PASS

# ====== 构建后端 ======
# 使用 python-for-android 作为构建工具
p4a.branch = master
# CPython 编译版本(若 p4a 升级可调整)
android.entrypoint = org.kivy.android.PythonActivity

# ====== 图标与启动图(可选,留空使用默认) ======
# icon.filename = icon.png
# presplash.filename = presplash.png

# ====== 日志 ======
log.level = 2

# ====== 构建选项 ======
# 并行编译(快)
android.ndk_api = 21
# 跳过已缓存下载,加快二次构建
warn_on_conflict = 0


[buildozer]

# 日志详细程度
log_level = 2
warn_on_root = 1

# 输出目录
build_dir = .buildozer

# 编译产物路径
bin_dir = bin
