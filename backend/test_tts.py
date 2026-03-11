"""
本地TTS功能测试脚本
"""
import os
import sys
from pathlib import Path
import base64
# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.tts import TTSService


def test_local_tts():
    """测试本地TTS服务"""
    print("=" * 50)
    print("测试本地TTS功能")
    print("=" * 50)
    
    # 创建输出目录
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    # 测试配置 - 先用一个简单的测试
    test_cases = [
        {"text": "你好，这是一段中文测试语音。", "language": "zh", "voice": "alloy"},
    ]
    
    # 初始化TTS服务（本地模型）
    tts_service = TTSService(
        provider="local",
        voice="alloy"
    )
    
    print(f"\nTTS服务提供商: {tts_service.provider}")
    print(f"TTS服务声音: {tts_service.voice}")
    print(f"TTS服务URL: {tts_service._synthesize_local.__code__.co_consts}")  # 显示URL常量
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    for i, case in enumerate(test_cases):
        print(f"\n测试 {i+1}/{len(test_cases)}:")
        print(f"  语言: {case['language']}")
        print(f"  文本: {case['text'][:30]}...")
        print(f"  声音: {case['voice']}")
        
        try:
            # 设置声音
            tts_service.voice = case["voice"]
            
            # 合成语音
            output_path = output_dir / f"test_{case['language']}_{case['voice']}.mp3"
            result = tts_service.synthesize(
                text=case["text"],
                output_path=str(output_path),
                language=case["language"]
            )
            
            # 检查文件
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"  ✓ 成功! 文件大小: {file_size} bytes")
                print(f"  ✓ 文件路径: {result}")
                
                # 检查文件是否有效（大于100字节）
                if file_size > 100:
                    print(f"  ✓ 文件看起来有效")
                else:
                    print(f"  ⚠ 文件可能无效（太小）")
            else:
                print(f"  ✗ 失败! 文件未生成")
                
        except Exception as e:
            import traceback
            print(f"  ✗ 错误: {str(e)}")
            print(f"  详细错误:")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print(f"输出文件目录: {output_dir}")
    print("=" * 50)


def test_voice_mapping():
    """测试声音映射"""
    print("\n" + "=" * 50)
    print("测试声音映射")
    print("=" * 50)
    
    from services.tts import LOCAL_VOICE_MAPPING
    
    print("\n声音映射关系:")
    print("-" * 30)
    for voice, source in LOCAL_VOICE_MAPPING.items():
        print(f"  {voice:10} -> voice_source: {source}")
    
    print("\n可用声音列表:")
    print("-" * 30)
    tts = TTSService(provider="local")
    voices = tts.get_available_voices()
    for v in voices:
        print(f"  {v['id']:10} - {v['name']} ({v['description']})")


def test_api_request():
    """测试API请求格式"""
    print("\n" + "=" * 50)
    print("测试API请求格式")
    print("=" * 50)
    
    import json
    from services.tts import LOCAL_TTS_URL, LOCAL_VOICE_MAPPING
    
    test_payload = {
        "text": "测试文本",
        "text_language": "zh",
        "voice_source": LOCAL_VOICE_MAPPING.get("alloy", "1"),
        "speed": 1,
        "base64": "True"
    }
    
    print(f"\nTTS API URL: {LOCAL_TTS_URL}")
    print(f"\n请求Payload:")
    print(json.dumps(test_payload, indent=2, ensure_ascii=False))


def test_api_direct():
    """直接测试TTS API，不经过服务层"""
    print("\n" + "=" * 50)
    print("直接测试TTS API")
    print("=" * 50)
    
    import requests
    import json
    from services.tts import LOCAL_TTS_URL, LOCAL_VOICE_MAPPING
    
    payload = {
        "text": "你好，这是直接API测试",
        "text_language": "zh",
        "voice_source": "1",
        "speed": 1,
        "base64": "True"
    }
    
    print(f"\n请求URL: {LOCAL_TTS_URL}")
    print(f"请求Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    print(f"\n注意: 使用的是 json=payload (application/json)")
    
    # 方法1: 使用json参数 (application/json)
    print("\n" + "-" * 50)
    print("方法1: POST json=payload")
    print("-" * 50)
    try:
        response = requests.post(LOCAL_TTS_URL, json=payload, timeout=60)
        print(f"请求头: {dict(response.request.headers)}")
        print(f"请求体: {response.request.body}")
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"✗ 失败: {e}")
    
    # 方法2: 使用data参数 (x-www-form-urlencoded)
    print("\n" + "-" * 50)
    print("方法2: POST data=payload (x-www-form-urlencoded)")
    print("-" * 50)
    try:
        response = requests.post(LOCAL_TTS_URL, data=payload, timeout=60)
        print(f"请求头: {dict(response.request.headers)}")
        print(f"请求体: {response.request.body}")
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"✗ 失败: {e}")
    
    # 方法3: 使用params参数 (GET请求)
    print("\n" + "-" * 50)
    print("方法3: GET params=payload")
    print("-" * 50)
    try:
        response = requests.get(LOCAL_TTS_URL, params=payload, timeout=60)
        print(f"请求头: {dict(response.request.headers)}")
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"✗ 失败: {e}")


if __name__ == "__main__":
    print("\n本地TTS功能测试")
    print("=" * 50)
    
    # 运行测试
    test_voice_mapping()
    test_api_request()
    
    # 询问是否直接测试API
    print("\n" + "=" * 50)
    response = input("\n是否直接测试TTS API（绕过服务层）? (y/n): ")
    if response.lower() == 'y':
        test_api_direct()
    
    # 询问是否进行实际TTS测试
    print("\n" + "=" * 50)
    response = input("\n是否通过服务层进行TTS测试? (y/n): ")
    if response.lower() == 'y':
        test_local_tts()
    else:
        print("跳过实际TTS调用测试")
