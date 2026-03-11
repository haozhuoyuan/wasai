import os
import base64
import tempfile
from pathlib import Path
from typing import Optional, List
import requests
import openai

# 本地TTS API配置（内置，不暴露给用户）
LOCAL_TTS_URL = "https://chat.gewu2030.com/gpu/tts_26/voice_cloning_api/74/"

# 本地TTS API的声音映射（voice -> voice_source）
# 注意：voice_source "36" 是Postman测试使用的有效值
LOCAL_VOICE_MAPPING = {
    "alloy": "36",    # 对应声音1
    "echo": "36",     # 对应声音2
    "fable": "36",    # 对应声音3
    "onyx": "36",     # 对应声音4
    "nova": "36",     # 对应声音5
    "shimmer": "36",  # 对应声音6
}


class TTSService:
    """文本转语音服务"""

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "tts-1",
        voice: str = "alloy",
        azure_key: Optional[str] = None,
        azure_region: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        self.voice = voice
        self.azure_key = azure_key
        self.azure_region = azure_region
        self.client = None

        if provider == "openai":
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url or "https://api.openai.com/v1"
            )

    def synthesize(self, text: str, output_path: str, language: str = "en") -> str:
        """
        合成语音

        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            language: 语言代码

        Returns:
            输出文件路径
        """
        if self.provider == "openai":
            return self._synthesize_openai(text, output_path)
        elif self.provider == "local":
            return self._synthesize_local(text, output_path, language)
        else:
            raise NotImplementedError(f"不支持的 TTS 提供商: {self.provider}")

    def _synthesize_openai(self, text: str, output_path: str) -> str:
        """使用 OpenAI TTS 合成语音"""
        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text
        )

        response.stream_to_file(output_path)
        return output_path

    def _synthesize_local(self, text: str, output_path: str, language: str = "en") -> str:
        """使用本地 TTS API 合成语音"""
        # 使用项目的目标语言作为 text_language
        # 支持的语言代码: zh, en, ja, ko, es, fr, de, ru, ar, pt, th, vi, id
        text_language = language

        # 获取 voice_source 映射
        voice_source = LOCAL_VOICE_MAPPING.get(self.voice, "1")

        payload = {
            "text": text,
            "text_language": text_language,
            "voice_source": voice_source,
            "speed": 1,
            "base64": "True"
        }

        try:
            response = requests.post(
                LOCAL_TTS_URL,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            
            # 调试日志（可以在生产环境移除）
            print(f"[TTS Debug] API Response: {data}")

            # 检查API返回是否成功
            if data.get("success") == "False" or data.get("code") != 200:
                raise RuntimeError(f"TTS API返回错误: {data.get('message', '未知错误')}")

            # 处理返回的base64音频数据
            if isinstance(data, dict):
                # 优先尝试常见的base64字段名
                audio_base64 = data.get("result") or data.get("audio") or data.get("data") or data.get("base64")
                
                if audio_base64 and isinstance(audio_base64, str):
                    audio_data = base64.b64decode(audio_base64)
                else:
                    raise ValueError(f"无法从响应中解析音频数据，字段缺失或格式错误: {data.keys()}")
            elif isinstance(data, str):
                # 如果直接返回base64字符串
                audio_data = base64.b64decode(data)
            else:
                raise ValueError(f"未知的响应格式: {type(data)}")

            # 写入文件
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            print(f"[TTS Debug] 音频文件已保存: {output_path}, 大小: {len(audio_data)} bytes")

            return output_path

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"本地 TTS 服务请求失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"TTS 处理失败: {str(e)}")

    def synthesize_subtitles(
        self,
        subtitles: List[dict],
        output_dir: str,
        language: str = "en"
    ) -> List[str]:
        """
        批量合成字幕音频

        Args:
            subtitles: 字幕列表，每项包含 translated_text
            output_dir: 输出目录
            language: 语言代码

        Returns:
            音频文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_paths = []
        for i, subtitle in enumerate(subtitles):
            text = subtitle.get("translated_text", "")
            if not text:
                audio_paths.append(None)
                continue

            output_path = output_dir / f"subtitle_{i:04d}.mp3"
            try:
                self.synthesize(text, str(output_path), language)
                audio_paths.append(str(output_path))
            except Exception as e:
                print(f"合成第 {i} 条字幕失败: {e}")
                audio_paths.append(None)

        return audio_paths

    def get_available_voices(self) -> List[dict]:
        """获取可用的语音列表"""
        # 所有支持的语音列表（OpenAI 和自定义API共用）
        voices = [
            {"id": "alloy", "name": "Alloy", "description": "中性声音"},
            {"id": "echo", "name": "Echo", "description": "男性声音"},
            {"id": "fable", "name": "Fable", "description": "男性声音"},
            {"id": "onyx", "name": "Onyx", "description": "男性声音"},
            {"id": "nova", "name": "Nova", "description": "女性声音"},
            {"id": "shimmer", "name": "Shimmer", "description": "女性声音"},
        ]

        if self.provider in ["openai", "local"]:
            return voices
        return []
