---
name: FFmpeg Media Processing
description: Use when user asks to convert, compress, trim, resize, extract audio, add subtitles, create GIFs, or process video/audio files
dependencies: ffmpeg
---

# FFmpeg Media Processing Skill

FFmpeg is a universal media converter that reads from multiple inputs, applies filters/transformations, and writes to multiple outputs.

## When to Use This Skill

Invoke this skill when the user wants to:
- Convert video/audio formats (MP4, MKV, WebM, MP3, etc.)
- Compress or resize videos
- Trim, cut, or merge media files
- Extract audio from video
- Add subtitles or text overlays
- Create GIFs from video
- Adjust speed, rotate, crop, or apply effects
- Stream media (HLS, DASH, RTMP)

## Example Inputs/Outputs

| User Says | Claude Does |
|-----------|-------------|
| "Convert video.mkv to mp4" | `ffmpeg -i video.mkv output.mp4` |
| "Extract audio from movie.mp4" | `ffmpeg -i movie.mp4 -vn audio.mp3` |
| "Compress this video" | `ffmpeg -i input.mp4 -crf 23 output.mp4` |
| "Make a GIF from the first 5 seconds" | `ffmpeg -t 5 -i input.mp4 -vf "fps=10,scale=320:-1" output.gif` |
| "Add subtitles to my video" | `ffmpeg -i input.mp4 -vf subtitles=subs.srt output.mp4` |

## Additional Resources

- **CONCEPTS.md** - Core concepts: video, audio, codecs, containers, processing pipeline
- **REFERENCE.md** - Complete command reference for all operations
- **ADVANCED.md** - Streaming (HLS/DASH/RTMP), complex filters, batch processing

---

## Synopsis

```
ffmpeg [global_options] {[input_file_options] -i input_url} ... {[output_file_options] output_url} ...
```

**IMPORTANT**: Order matters! Options apply to the next specified file and reset between files.

---

## Quick Reference - Main Options

| Option | Purpose |
|--------|---------|
| `-i url` | Specify input file |
| `-c copy` | Stream copy (no re-encode, fast) |
| `-c:v codec` | Set video codec (libx264, libx265, libvpx-vp9) |
| `-c:a codec` | Set audio codec (aac, libmp3lame, libopus) |
| `-vf filter` | Apply video filter |
| `-af filter` | Apply audio filter |
| `-ss time` | Seek to position |
| `-t duration` | Limit duration |
| `-y` | Overwrite output |
| `-vn` | No video |
| `-an` | No audio |

---

## Most Common Commands

### Convert Format
```bash
ffmpeg -i input.mkv output.mp4
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm
```

### Extract Audio
```bash
ffmpeg -i video.mp4 -vn -c:a copy audio.aac
ffmpeg -i video.mp4 -vn -c:a libmp3lame -b:a 192k audio.mp3
```

### Compress Video
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a copy output.mp4
```

### Trim/Cut
```bash
ffmpeg -ss 00:01:00 -i input.mp4 -t 00:00:30 -c copy output.mp4
```

### Resize
```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
ffmpeg -i input.mp4 -vf scale=640:-1 output.mp4
```

### Create GIF
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1" output.gif
```

### Add Text
```bash
ffmpeg -i input.mp4 -vf "drawtext=text='Hello':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" output.mp4
```

### Burn Subtitles
```bash
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4
```

### Extract Frames
```bash
ffmpeg -i input.mp4 -vf fps=1 frame_%04d.png
```

### Speed Up/Slow Down
```bash
# 2x speed
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" output.mp4
```

### Merge Files
```bash
# Create filelist.txt with: file 'part1.mp4' (one per line)
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

---

## Video Options

| Option | Purpose |
|--------|---------|
| `-r fps` | Set frame rate |
| `-s WxH` | Set resolution |
| `-crf N` | Quality (0-51, lower=better, default 23) |
| `-b:v bitrate` | Set video bitrate |
| `-preset name` | Encoding speed (ultrafast to veryslow) |

## Audio Options

| Option | Purpose |
|--------|---------|
| `-ar freq` | Sample rate (44100, 48000) |
| `-ac N` | Channels (1=mono, 2=stereo) |
| `-b:a bitrate` | Audio bitrate |

---

## Common Filters

| Filter | Example | Purpose |
|--------|---------|---------|
| scale | `scale=1280:720` | Resize |
| crop | `crop=640:480:100:50` | Crop (w:h:x:y) |
| transpose | `transpose=1` | Rotate 90° CW |
| hflip/vflip | `hflip` | Mirror |
| fade | `fade=t=in:d=2` | Fade in/out |
| drawtext | `drawtext=text='Hi'` | Text overlay |
| subtitles | `subtitles=subs.srt` | Burn subtitles |
| overlay | `overlay=10:10` | Image overlay |

---

## File Info

```bash
ffprobe input.mp4
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

---

## Best Practices

1. Use `-c copy` when possible (fast, no quality loss)
2. Place `-ss` before `-i` for fast seeking
3. Use `-y` to overwrite without prompts
4. Use `-crf 18-28` for quality control
5. Check file info with `ffprobe` first

---

For complete reference, see **REFERENCE.md**, **CONCEPTS.md**, and **ADVANCED.md**.
