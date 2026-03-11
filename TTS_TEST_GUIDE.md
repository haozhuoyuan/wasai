# 本地TTS功能测试指南

## 一、快速测试（推荐）

### 1. 直接测试TTS服务（无需启动后端）

```bash
cd backend
conda run -n wasai python test_tts.py
```

这个测试会：
- 显示声音映射关系
- 显示API请求格式
- 询问是否进行实际TTS调用

如果TTS服务器可用，输入 `y` 会进行实际的语音合成测试。

### 2. 测试API接口（需要启动后端）

**步骤1: 启动后端服务**
```bash
cd backend
conda run -n wasai uvicorn main:app --reload
```

**步骤2: 运行API测试脚本**
```bash
# 新开个终端
cd backend
conda run -n wasai python test_api.py
```

## 二、手动完整流程测试

### 步骤1: 启动服务

```bash
# 终端1: 启动后端
cd backend
uvicorn main:app --reload

# 终端2: 启动前端
cd frontend
npm run dev
```

### 步骤2: 配置TTS设置

1. 打开浏览器访问 http://localhost:5173
2. 点击左侧菜单 "设置"
3. 切换到 "语音合成 (TTS)" 标签
4. 选择 "本地模型"
5. 选择一个声音（声音1-6）
6. 点击 "保存设置"

### 步骤3: 创建项目

1. 点击左侧菜单 "工作台"
2. 点击 "新建项目"
3. 输入项目名称
4. **重要**: 设置 "目标语言" 为你想要测试的语言（如英语、日语等）
5. 点击 "创建"

### 步骤4: 上传视频

1. 点击项目卡片进入详情
2. 上传一个测试视频（带语音的）
3. 等待上传完成

### 步骤5: 语音识别 (ASR)

1. 点击 "开始识别"
2. 等待识别完成，看到字幕列表

### 步骤6: 翻译字幕

1. 点击 "自动翻译"
2. 等待翻译完成，或手动编辑字幕

### 步骤7: 生成配音（测试TTS）

1. 点击 "生成配音"
2. 等待TTS合成完成
3. 检查音频文件是否生成

**检查生成的音频:**
```bash
# 音频文件位置
backend/uploads/project_{项目ID}/audio/subtitle_*.mp3
```

## 三、验证TTS参数

你可以添加日志来验证参数是否正确传递。修改 `backend/services/tts.py`:

```python
def _synthesize_local(self, text: str, output_path: str, language: str = "en") -> str:
    # ... 在方法开始处添加日志
    print(f"[TTS Debug] language={language}, voice={self.voice}")
    print(f"[TTS Debug] text={text[:20]}...")
    # ...
    print(f"[TTS Debug] payload={payload}")
```

## 四、常见问题

### Q1: TTS服务器连接失败

**现象**: `本地 TTS 服务请求失败: ...`

**解决**:
- 确认TTS服务器 `http://10.5.5.55:9876` 可访问
- 检查防火墙设置
- 测试: `curl http://10.5.5.55:9876/tts_26/voice_cloning_api/74/`

### Q2: 语言代码不匹配

**现象**: TTS服务器返回错误或不正确的语音

**检查**:
- 前端语言代码: `zh`, `en`, `ja`, `ko`, `es`, `fr`, `de`, `ru`, `ar`, `pt`, `th`, `vi`, `id`
- 确认TTS服务器支持这些语言代码
- 查看 `backend/services/tts.py` 中的 `text_language` 值

### Q3: 生成的音频播放不了

**现象**: 音频文件生成但无法播放

**解决**:
- 检查文件大小（应该 > 1KB）
- 检查文件格式（应该是MP3）
- 使用 `ffprobe` 查看文件信息:
  ```bash
  ffprobe -v error backend/uploads/project_1/audio/subtitle_0000.mp3
  ```

## 五、测试检查清单

- [ ] 后端服务启动无错误
- [ ] 前端可以正常访问
- [ ] 设置页面可以切换到 "本地模型"
- [ ] 创建项目时目标语言设置正确
- [ ] 上传视频成功
- [ ] ASR识别成功
- [ ] 翻译成功
- [ ] TTS生成配音成功
- [ ] 音频文件生成且可播放
- [ ] 音频语言与目标语言一致
