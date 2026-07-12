#!/usr/bin/env python3
"""
环保智慧执法平台 — AI短视频生成引擎
功能：根据执法数据、工作成果自动生成汇报/宣传短视频
技术：FFmpeg + TTS + LLM叙事脚本
"""

import os
import json
import subprocess
import tempfile
from datetime import datetime

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
VIDEO_DIR = os.path.join(OUTPUTS_DIR, 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)


def generate_video_script(data, video_type='enforcement'):
    """
    根据数据生成视频脚本
    video_type: enforcement(执法纪实), report(工作汇报), public(公众宣传)
    """
    templates = {
        'enforcement': {
            'opening': '近日，{org}执法人员在{location}开展现场检查，',
            'body': '检查发现{findings}。执法人员立即{actions}，',
            'evidence': '现场采集证据{evidence_count}项，包括{evidence_list}。',
            'closing': '目前案件正在进一步调查处理中。{org}将持续严厉打击环境违法行为，守护碧水蓝天。',
        },
        'report': {
            'opening': '{period}，{org}共开展执法检查{check_count}次，',
            'body': '发现环境违法问题{violation_count}个，立案处罚{case_count}件，',
            'highlights': '其中，{highlights}。',
            'closing': '下一步，{org}将继续加大执法力度，确保环境安全。',
        },
        'public': {
            'opening': '保护环境，人人有责。',
            'body': '{org}提醒广大市民，如发现环境违法行为，请拨打12369环保举报热线。',
            'tips': '日常生活中，我们可以{tips}。',
            'closing': '让我们共同守护绿水青山，共建美丽家园。',
        }
    }

    template = templates.get(video_type, templates['enforcement'])
    script = {}

    for key, fmt in template.items():
        try:
            script[key] = fmt.format(**data)
        except (KeyError, IndexError):
            script[key] = fmt

    return script


def generate_subtitle_srt(segments, output_path):
    """生成SRT字幕文件"""
    lines = []
    for i, seg in enumerate(segments):
        start = seg.get('start', '00:00:00,000')
        end = seg.get('end', '00:00:03,000')
        text = seg.get('text', '')
        lines.append(f'{i + 1}')
        lines.append(f'{start} --> {end}')
        lines.append(text)
        lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def create_video_from_images(images, audio_path, subtitles_path, output_path, duration_per_image=5):
    """
    从图片序列+音频+字幕合成视频
    images: 图片路径列表
    audio_path: 音频文件路径
    subtitles_path: SRT字幕文件路径
    output_path: 输出视频路径
    """
    if not images:
        return None

    # 创建图片列表文件
    list_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    for img in images:
        list_file.write(f"file '{img}'\n")
        list_file.write(f"duration {duration_per_image}\n")
    # FFmpeg concat demuxer 需要最后一行重复
    list_file.write(f"file '{images[-1]}'\n")
    list_file.close()

    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', list_file.name,
            '-i', audio_path,
            '-vf', f"subtitles={subtitles_path}",
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '128k',
            '-shortest',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None
        return output_path
    except FileNotFoundError:
        print("FFmpeg not installed, creating placeholder")
        return None
    except subprocess.TimeoutExpired:
        print("FFmpeg timeout")
        return None
    finally:
        os.unlink(list_file.name)


def create_slideshow_video(text_content, output_path, bg_color='#1B4332', font_size=36, duration=10):
    """
    创建文字幻灯片视频（无需图片素材）
    用于快速生成汇报视频
    """
    try:
        # 检查ffmpeg是否可用
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # FFmpeg不可用，生成视频描述JSON
        video_desc = {
            'type': 'slideshow',
            'text': text_content,
            'bg_color': bg_color,
            'font_size': font_size,
            'duration': duration,
            'created_at': datetime.now().isoformat(),
            'note': 'FFmpeg未安装，已生成视频描述文件。安装FFmpeg后可生成实际视频。'
        }
        desc_path = output_path.replace('.mp4', '.json')
        with open(desc_path, 'w', encoding='utf-8') as f:
            json.dump(video_desc, f, ensure_ascii=False, indent=2)
        return desc_path

    # 分段文字
    segments = text_content.split('\n') if '\n' in text_content else [text_content]

    # 使用FFmpeg drawtext滤镜
    filters = []
    for i, seg in enumerate(segments):
        if not seg.strip():
            continue
        start = i * duration
        end = (i + 1) * duration
        escaped = seg.replace("'", "\\'").replace(":", "\\:").replace("=", "\\=")
        filters.append(
            f"drawtext=text='{escaped}':"
            f"fontcolor=white:fontsize={font_size}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='between(t,{start},{end})'"
        )

    filter_str = ','.join(filters) if filters else "drawtext=text='环保智慧执法平台':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2"

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', f'color=c={bg_color}:s=1920x1080:d={duration * len(segments)}:r=25',
        '-vf', filter_str,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-t', str(duration * len(segments)),
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        return output_path
    else:
        print(f"FFmpeg error: {result.stderr}")
        return None


def generate_enforcement_video(case_data):
    """生成执法纪实视频"""
    script = generate_video_script(case_data, 'enforcement')

    narration = ' '.join(script.values())

    # 暂时生成视频描述文件
    result = {
        'type': 'enforcement',
        'script': script,
        'narration': narration,
        'status': 'script_ready',
        'created_at': datetime.now().isoformat(),
        'next_steps': [
            '1. TTS生成旁白音频',
            '2. 整理现场照片/视频素材',
            '3. FFmpeg合成最终视频'
        ]
    }

    filename = f'enforcement_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    filepath = os.path.join(VIDEO_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return filepath


def generate_report_video(report_data):
    """生成工作汇报视频"""
    script = generate_video_script(report_data, 'report')
    narration = ' '.join(script.values())

    # 生成幻灯片式视频描述
    slides = []
    for key, text in script.items():
        slides.append({
            'type': 'text_slide',
            'content': text,
            'duration': 5,
            'style': {
                'bg': '#1B4332' if key in ('opening', 'closing') else '#FFFFFF',
                'color': '#FFFFFF' if key in ('opening', 'closing') else '#1A1A1A',
            }
        })

    result = {
        'type': 'report',
        'script': script,
        'narration': narration,
        'slides': slides,
        'status': 'script_ready',
        'created_at': datetime.now().isoformat(),
    }

    filename = f'report_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    filepath = os.path.join(VIDEO_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return filepath


def generate_public_video(topic_data):
    """生成公众宣传视频"""
    script = generate_video_script(topic_data, 'public')
    narration = ' '.join(script.values())

    result = {
        'type': 'public',
        'script': script,
        'narration': narration,
        'status': 'script_ready',
        'created_at': datetime.now().isoformat(),
    }

    filename = f'public_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    filepath = os.path.join(VIDEO_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return filepath


if __name__ == '__main__':
    # 测试
    test_data = {
        'org': '济南市生态环境局',
        'location': '某化工园区',
        'findings': '某化工厂私设暗管排放含重金属废水，超标5倍以上',
        'actions': '固定证据、立案调查',
        'evidence_count': '12',
        'evidence_list': '现场照片、水样检测报告、暗管位置图、监控视频',
    }
    result = generate_enforcement_video(test_data)
    print(f'✅ 视频脚本已生成: {result}')
