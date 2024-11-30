import os
import json
import asyncio
from typing import List, Dict, AsyncGenerator
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
import dotenv
import datetime
from fastapi.responses import StreamingResponse
import shutil


dotenv.load_dotenv()

# 使用相對路徑
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_AUDIO_DIR = os.path.join(BACKEND_DIR, "stores", "audio")

class VoiceProfile:
    def __init__(self, role: str, voice_name: str, speed: float = 1.0, pitch: int = 0):
        self.role = role
        self.voice_name = voice_name
        self.speed = speed
        self.pitch = pitch

class VoiceConfig:
    def __init__(self, host_voice: str = "zh-TW-HsiaoChenNeural", 
                 guest_voice: str = "zh-TW-YunJheNeural",
                 host_speed: float = 1.0,
                 guest_speed: float = 1.0,
                 host_pitch: int = 0,
                 guest_pitch: int = 0):
        """
        初始化語音設定
        
        Args:
            host_voice: 主持人的語音，預設為女聲 HsiaoChen
            guest_voice: 來賓的語音，預設為男聲 YunJhe
            host_speed: 主持人語速 (0.5-2.0)
            guest_speed: 來賓語速 (0.5-2.0)
            host_pitch: 主持人音調 (-10 到 10)
            guest_pitch: 來賓音調 (-10 到 10)
        """
        self.profiles = {
            "主持人": VoiceProfile("主持人", host_voice, host_speed, host_pitch),
            "來賓": VoiceProfile("來賓", guest_voice, guest_speed, guest_pitch),
        }

class PodcastSynthesizer:
    def __init__(self, output_dir: str = DEFAULT_AUDIO_DIR, 
                 host_voice: str = "zh-TW-HsiaoChenNeural",
                 guest_voice: str = "zh-TW-YunJheNeural"):
        self.voice_config = VoiceConfig(host_voice, guest_voice)
        self.output_dir = output_dir
        self.temp_dir = os.path.join(output_dir, "temp")
        self.segments_dir = os.path.join(output_dir, "segments")
        print(f"輸出目錄：{self.output_dir}")
        print(f"暫存目錄：{self.temp_dir}")
        print(f"段落音檔目錄：{self.segments_dir}")
        self._ensure_directories()
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get('SPEECH_KEY'),
            region=os.environ.get('SPEECH_REGION')
        )
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
        )

    def _ensure_directories(self):
        """確保所有需要的目錄存在"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.segments_dir, exist_ok=True)

    def synthesize_segment(self, text: str, voice_name: str, output_file: str, speed: float = 1.0, pitch: int = 0) -> bool:
        """合成單一段落的語音"""
        try:
            print(f"\n正在合成語音段落:")
            print(f"- 使用語音: {voice_name}")
            print(f"- 語速: {speed}")
            print(f"- 音調: {pitch}")
            print(f"- 文本內容: {text[:50]}...")
            print(f"- 輸出檔案: {output_file}")

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )

            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">
                <voice name="{voice_name}">
                    <prosody rate="{speed}" pitch="{pitch}st">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            print(f"- SSML內容:\n{ssml}")

            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                with open(output_file, "wb") as audio_file:
                    audio_file.write(result.audio_data)
                print("✓ 語音合成成功")
                return True
            else:
                print(f"✗ 語音合成失敗：{result.reason}")
                if result.reason == speechsdk.ResultReason.Canceled:
                    details = result.cancellation_details
                    print(f"✗ 取消原因: {details.reason}")
                    print(f"✗ 錯誤詳情: {details.error_details}")
                    print(f"✗ 錯誤代碼: {details.error_code}")
                return False
                
        except Exception as e:
            print(f"✗ 發生異常: {str(e)}")
            import traceback
            print(f"✗ 詳細錯誤:\n{traceback.format_exc()}")
            return False

    def merge_audio_files(self, audio_files: List[str], output_file: str):
        """合併多個音檔"""
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            segment = AudioSegment.from_wav(audio_file)
            combined += segment
            # 在每段之間加入 0.5 秒的靜音
            combined += AudioSegment.silent(duration=500)
        
        combined.export(output_file, format="wav")

    def generate_podcast(self, script_data: Dict, filename: str = None) -> Dict:
        """生成 Podcast 音檔，並將音檔路徑加入原始腳本資料中"""
        try:
            temp_files = []
            
            # 使用時間戳建立本次生成的目錄
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            session_dir = os.path.join(self.segments_dir, timestamp)
            os.makedirs(session_dir, exist_ok=True)

            # 取得主持人和來賓的名稱，用於判斷說話者角色
            host_name = script_data.get("host_name", "主持人")
            guest_name = script_data.get("guest_name", "來賓")

            # 處理每個對話段落
            for i, segment in enumerate(script_data["dialogue"]):
                speaker = segment["speaker"]
                content = segment["content"]
                
                # 根據說話者名稱判斷使用哪個語音配置
                if speaker == host_name:
                    voice_profile = self.voice_config.profiles["主持人"]
                else:
                    voice_profile = self.voice_config.profiles["來賓"]
                
                # 生成臨時檔案路徑
                temp_file = os.path.join(self.temp_dir, f"segment_{i}.wav")
                temp_files.append(temp_file)
                
                # 生成最終段落檔路徑，改用簡單的編號格式
                segment_filename = f"segment_{i:03d}.wav"
                segment_file = os.path.join(session_dir, segment_filename)
                
                success = self.synthesize_segment(
                    content,
                    voice_profile.voice_name,
                    temp_file,
                    voice_profile.speed,
                    voice_profile.pitch
                )
                
                if not success:
                    raise Exception(f"合成失敗：第 {i+1} 段對話")
                
                # 複製臨時檔案到段落目錄
                import shutil
                shutil.copy2(temp_file, segment_file)
                
                # 將音檔路徑加入到對話資料中
                script_data["dialogue"][i]["audio_file"] = segment_file

            # 生成完整音檔路徑
            if filename:
                final_output = os.path.join(self.output_dir, filename)
            else:
                final_output = os.path.join(self.output_dir, f"podcast_{timestamp}.wav")
            
            # 合併所有音檔
            self.merge_audio_files(temp_files, final_output)
            
            # 清理臨時檔案
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # 將完整音檔路徑加入到腳本資料中
            script_data["full_audio"] = final_output
            
            # 檢查檔案是否都成功生成
            if os.path.exists(final_output):
                print(f"完整音檔已生成：{final_output}")
                print(f"檔案大小：{os.path.getsize(final_output)} bytes")
                print(f"分段音檔目錄：{session_dir}")
            else:
                print(f"警告：完整音檔未成功生成於 {final_output}")
            
            return script_data
            
        except Exception as e:
            print(f"Podcast 生成失敗：{str(e)}")
            raise

    async def synthesize_segment_stream(self, text: str, voice_name: str) -> AsyncGenerator[bytes, None]:
        """串流式合成單一段落的語音"""
        try:
            print(f"\n正在合成語音段落:")
            print(f"- 使用語音: {voice_name}")
            print(f"- 文本內容: {text[:50]}...")

            # 建立串流合成器
            stream = speechsdk.AudioOutputStream()
            audio_config = speechsdk.audio.AudioOutputConfig(stream=stream)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">
                <voice name="{voice_name}">
                    {text}
                </voice>
            </speak>
            """

            # 設定串流回調
            buffer_size = 4096  # 4KB 緩衝區
            audio_buffer = bytes()

            def handle_audio_data(evt):
                nonlocal audio_buffer
                audio_buffer += evt.result.audio_data
                if len(audio_buffer) >= buffer_size:
                    # 當緩衝區達到指定大小時回傳
                    chunk = audio_buffer[:buffer_size]
                    audio_buffer = audio_buffer[buffer_size:]
                    return chunk

            # 註冊事件處理器
            synthesizer.synthesizing.connect(handle_audio_data)
            
            # 開始合成
            result = await synthesizer.speak_ssml_async(ssml)
            
            # 回傳剩餘的音訊數據
            if audio_buffer:
                yield audio_buffer

        except Exception as e:
            print(f"✗ 串流合成失敗: {str(e)}")
            raise

    async def generate_podcast_stream(self, script_data: Dict) -> AsyncGenerator[Dict, None]:
        """串流生成 Podcast，一次生成一個段落並立即回傳"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            segments_dir = os.path.join(self.segments_dir, timestamp)
            os.makedirs(segments_dir, exist_ok=True)

            host_name = script_data.get("host_name", "主持人")
            guest_name = script_data.get("guest_name", "來賓")

            yield {
                "type": "start",
                "total_segments": len(script_data["dialogue"]),
                "session_dir": segments_dir
            }

            for i, segment in enumerate(script_data["dialogue"]):
                try:
                    speaker = segment["speaker"]
                    content = segment["content"]
                    
                    # 選擇語音配置 - 第一個說話者永遠使用主持人的語音
                    voice_profile = (
                        self.voice_config.profiles["主持人"] 
                        if i == 0 or speaker == host_name 
                        else self.voice_config.profiles["來賓"]
                    )

                    # 生成段落音檔
                    segment_filename = f"segment_{i:03d}.wav"
                    segment_file = os.path.join(segments_dir, segment_filename)
                    
                    # 開始處理前先回報
                    yield {
                        "type": "progress",
                        "index": i,
                        "total": len(script_data["dialogue"]),
                        "speaker": speaker,
                        "content": content
                    }

                    success = self.synthesize_segment(
                        content,
                        voice_profile.voice_name,
                        segment_file,
                        voice_profile.speed,
                        voice_profile.pitch
                    )

                    if success:
                        # 儲存音頻檔案
                        with open(segment_file, "wb") as f:
                            f.write(result.audio_data)
                        
                        # 生成相對 URL 路徑
                        relative_url = f"/audio/segments/{timestamp}/{segment_filename}"
                        print(f"音頻檔案路徑: {segment_file}")
                        print(f"音頻 URL: {relative_url}")
                        
                        yield {
                            "type": "audio",
                            "index": i,
                            "total": len(script_data["dialogue"]),
                            "speaker": speaker,
                            "content": content,
                            "audio_file": relative_url  # 使用相對 URL
                        }
                    else:
                        yield {
                            "type": "error",
                            "index": i,
                            "message": f"第 {i+1} 段語音生成失敗"
                        }

                except Exception as e:
                    yield {
                        "type": "error",
                        "index": i,
                        "message": str(e)
                    }

        except Exception as e:
            yield {
                "type": "error",
                "message": f"生成過程發生錯誤: {str(e)}"
            }

    async def generate_segment(self, text: str, voice_name: str, output_file: str) -> bool:
        """非阻塞的語音合成"""
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config, 
                audio_config=None
            )

            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">
                <voice name="{voice_name}">
                    {text}
                </voice>
            </speak>
            """

            # 使用 asyncio 來非阻塞地等待結果
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: synthesizer.speak_ssml_async(ssml).get()
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                with open(output_file, "wb") as audio_file:
                    audio_file.write(result.audio_data)
                return True
            return False

        except Exception as e:
            print(f"語音合成失敗：{str(e)}")
            return False

    async def process_segments(self, script_data: Dict):
        """使用異步方式處理所有段落"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(self.segments_dir, timestamp)
        os.makedirs(session_dir, exist_ok=True)

        host_name = script_data.get("host_name", "主持人")
        guest_name = script_data.get("guest_name", "來賓")

        print(f"開始處理對話段落")
        print(f"使用語音設定 - 主持人: {self.voice_config.profiles['主持人'].voice_name}")
        print(f"使用語音設定 - 來賓: {self.voice_config.profiles['來賓'].voice_name}")

        for i, segment in enumerate(script_data["dialogue"]):
            try:
                speaker = segment["speaker"]
                content = segment["content"]
                
                # 根據說話者選擇語音
                voice_profile = (
                    self.voice_config.profiles["主持人"] 
                    if speaker == host_name 
                    else self.voice_config.profiles["來賓"]
                )
                
                print(f"\n處理第 {i+1} 段對話:")
                print(f"- 說話者: {speaker}")
                print(f"- 使用語音: {voice_profile.voice_name}")

                # 生成檔案路徑
                segment_filename = f"segment_{i:03d}.wav"
                segment_file = os.path.join(session_dir, segment_filename)
                
                # 開始處理前先回報
                yield {
                    "type": "progress",
                    "status": "processing",
                    "index": i,
                    "total": len(script_data["dialogue"]),
                    "speaker": speaker,
                    "content": content,
                    "voice": voice_profile.voice_name
                }

                # 生成語音
                success = await self.generate_segment(
                    content,
                    voice_profile.voice_name,
                    segment_file
                )

                if success:
                    relative_url = f"/audio/segments/{timestamp}/segment_{i:03d}.wav"
                    yield {
                        "type": "audio",
                        "status": "success",
                        "index": i,
                        "total": len(script_data["dialogue"]),
                        "speaker": speaker,
                        "content": content,
                        "audio_file": relative_url,
                        "voice": voice_profile.voice_name
                    }
                else:
                    yield {
                        "type": "error",
                        "status": "error",
                        "index": i,
                        "message": f"第 {i+1} 段語音生成失敗"
                    }
            except Exception as e:
                print(f"處理段落 {i+1} 時發生錯誤: {str(e)}")
                yield {
                    "type": "error",
                    "index": i,
                    "message": str(e)
                }

def synthesize_podcast(
    script_data: Dict, 
    output_dir: str = DEFAULT_AUDIO_DIR, 
    filename: str = None,
    host_voice: str = "zh-TW-HsiaoChenNeural",
    guest_voice: str = "zh-TW-YunJheNeural"
) -> Dict:
    """
    便捷函數用於生成 Podcast
    
    Args:
        script_data: 腳本資料
        output_dir: 輸出目錄
        filename: 輸出檔案名稱
        host_voice: 主持人的語音
        guest_voice: 來賓的語音
    """
    synthesizer = PodcastSynthesizer(
        output_dir=output_dir,
        host_voice=host_voice,
        guest_voice=guest_voice
    )
    return synthesizer.generate_podcast(script_data, filename)

# 測試程式
if __name__ == "__main__":
    test_script = {
        "dialogue": [
            {
                "speaker": "主持人",
                "content": "大家好，歡迎來到我們的Podcast！"
            },
            {
                "speaker": "來賓",
                "content": "很高興能來到這裡。"
            }
        ],
        "host_name": "主持人",
        "guest_name": "來賓"
    }
    
    try:
        # 使用不同的語音設定
        output_file = synthesize_podcast(
            test_script,
            host_voice="zh-TW-HsiaoYuNeural",    # 使用小玉的聲音當主持人
            guest_voice="zh-TW-YunJheNeural"   # 使用雲哲的聲音當來賓
        )
        print(f"Podcast 已成功生成：{output_file}")
    except Exception as e:
        print(f"生成失敗：{str(e)}")