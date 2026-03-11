"""
API接口测试脚本
需要先启动后端服务: uvicorn main:app --reload
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_settings_api():
    """测试设置API"""
    print("=" * 50)
    print("测试设置API")
    print("=" * 50)
    
    # 获取设置
    try:
        resp = requests.get(f"{BASE_URL}/api/settings/")
        print(f"\n1. 获取所有设置:")
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   TTS提供商: {data.get('tts_provider')}")
            print(f"   TTS声音: {data.get('tts_voice')}")
            print("   ✓ 成功")
        else:
            print(f"   ✗ 失败: {resp.text}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    # 更新设置为本地模型
    try:
        print(f"\n2. 更新TTS设置为本地模型:")
        resp = requests.get(f"{BASE_URL}/api/settings/")
        settings = resp.json()
        settings['tts_provider'] = 'local'
        settings['tts_voice'] = 'alloy'
        
        resp = requests.put(f"{BASE_URL}/api/settings/", json=settings)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   ✓ 成功")
        else:
            print(f"   ✗ 失败: {resp.text}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    # 获取TTS设置
    try:
        resp = requests.get(f"{BASE_URL}/api/settings/tts")
        print(f"\n3. 获取TTS设置:")
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   响应: {json.dumps(resp.json(), indent=2)}")
            print("   ✓ 成功")
        else:
            print(f"   ✗ 失败: {resp.text}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")


def test_workflow_api(project_id=1):
    """测试工作流API - 需要已有项目"""
    print("\n" + "=" * 50)
    print("测试工作流API")
    print("=" * 50)
    
    # 测试TTS接口
    try:
        print(f"\n1. 测试TTS接口 (项目ID: {project_id}):")
        resp = requests.post(
            f"{BASE_URL}/api/workflow/{project_id}/tts",
            json={"language": "zh"}  # 这个参数现在应该被忽略了，使用项目的目标语言
        )
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            print("   ✓ 成功")
        else:
            print(f"   ✗ 失败: {resp.text[:200]}")
            print("   提示: 需要先创建项目并上传视频、完成翻译")
    except Exception as e:
        print(f"   ✗ 错误: {e}")


def test_projects_api():
    """测试项目API"""
    print("\n" + "=" * 50)
    print("测试项目API")
    print("=" * 50)
    
    try:
        resp = requests.get(f"{BASE_URL}/api/projects/")
        print(f"\n1. 获取项目列表:")
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            projects = resp.json()
            print(f"   项目数量: {len(projects)}")
            for p in projects[:3]:  # 只显示前3个
                print(f"   - ID:{p['id']} {p['name']} [{p['source_language']}>{p['target_language']}]")
            if projects:
                return projects[0]['id']
        else:
            print(f"   ✗ 失败: {resp.text}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    return None


def create_test_project():
    """创建测试项目"""
    print("\n" + "=" * 50)
    print("创建测试项目")
    print("=" * 50)
    
    try:
        project_data = {
            "name": "TTS测试项目",
            "description": "用于测试本地TTS功能",
            "source_language": "zh",
            "target_language": "en"  # 目标语言设为英语
        }
        
        resp = requests.post(f"{BASE_URL}/api/projects/", json=project_data)
        print(f"\n创建项目:")
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 201:
            data = resp.json()
            print(f"   项目ID: {data['id']}")
            print(f"   源语言: {data['source_language']}")
            print(f"   目标语言: {data['target_language']}")
            print("   ✓ 成功")
            return data['id']
        else:
            print(f"   ✗ 失败: {resp.text}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    return None


if __name__ == "__main__":
    print("\nAPI接口测试")
    print("=" * 50)
    print(f"BASE_URL: {BASE_URL}")
    print("=" * 50)
    
    # 测试设置API
    test_settings_api()
    
    # 获取项目列表
    project_id = test_projects_api()
    
    if project_id:
        # 测试工作流
        test_workflow_api(project_id)
    else:
        print("\n没有现有项目，是否创建测试项目?")
        response = input("(y/n): ")
        if response.lower() == 'y':
            new_id = create_test_project()
            if new_id:
                print(f"\n项目创建成功，ID: {new_id}")
                print("请先上传视频并完成翻译后再测试TTS功能")
