# FFmpeg Command Reference

## Complete Options Reference

### Main Options
| Option | Purpose |
|--------|---------|
| `-i url` | Specify input file |
| `-f fmt` | Force input/output format |
| `-c[:stream] codec` | Select encoder/decoder (or `copy`) |
| `-t duration` | Limit output duration |
| `-ss position` | Seek to position |
| `-to position` | Stop writing at position |
| `-y` | Overwrite output files |
| `-n` | Never overwrite |
| `-map input:stream` | Manually select streams |

### Video Options
| Option | Purpose |
|--------|---------|
| `-r fps` | Set frame rate |
| `-s WxH` | Set frame size (e.g., 1920x1080) |
| `-aspect ratio` | Set aspect ratio (e.g., 16:9) |
| `-vf filtergraph` | Apply video filter chain |
| `-vn` | Disable video output |
| `-vcodec codec` | Set video codec |
| `-b:v bitrate` | Set video bitrate |
| `-crf value` | Quality (0-51, lower=better) |
| `-pix_fmt format` | Set pixel format |
| `-frames:v N` | Output N video frames |

### Audio Options
| Option | Purpose |
|--------|---------|
| `-ar freq` | Sample rate (44100, 48000) |
| `-ac channels` | Number of channels |
| `-af filtergraph` | Apply audio filter chain |
| `-an` | Disable audio output |
| `-acodec codec` | Set audio codec |
| `-b:a bitrate` | Set audio bitrate |

### Subtitle Options
| Option | Purpose |
|--------|---------|
| `-sn` | Disable subtitles |
| `-scodec codec` | Set subtitle codec |

### Global Options
| Option | Purpose |
|--------|---------|
| `-loglevel level` | quiet, error, warning, info, verbose, debug |
| `-hide_banner` | Suppress banner |
| `-stats` | Show progress |
| `-benchmark` | Show performance |
| `-report` | Dump logs to file |

---

## Stream Selection & Mapping

```bash
# Stream specifier: input_index:stream_type:stream_index
# Types: v=video, a=audio, s=subtitle

# Select all streams from input 0
ffmpeg -i input.mkv -map 0 output.mp4

# Video from input 0, audio from input 1
ffmpeg -i video.mp4 -i audio.mp3 -map 0:v -map 1:a output.mp4

# Second audio stream
ffmpeg -i input.mkv -map 0:a:1 output.mp3

# All except subtitles
ffmpeg -i input.mkv -map 0 -map -0:s output.mp4
```

---

## Format Conversion

```bash
# Basic conversion
ffmpeg -i input.mkv output.mp4

# Specify codecs
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4

# To WebM
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm

# Audio conversion
ffmpeg -i input.wav -c:a libmp3lame -b:a 320k output.mp3
ffmpeg -i input.mp3 -c:a flac output.flac
```

---

## Extract Audio

```bash
# Stream copy (fastest)
ffmpeg -i video.mp4 -vn -c:a copy audio.aac

# Re-encode to MP3
ffmpeg -i video.mp4 -vn -c:a libmp3lame -b:a 192k audio.mp3

# To WAV (uncompressed)
ffmpeg -i video.mp4 -vn audio.wav
```

---

## Compress Video

```bash
# CRF mode (18-28 recommended)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a copy output.mp4

# Two-pass encoding
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 1 -an -f null NUL
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 2 -c:a aac output.mp4

# Constrained bitrate
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -maxrate 1.5M -bufsize 2M output.mp4
```

---

## Trim/Cut Media

```bash
# Fast seek + cut
ffmpeg -ss 00:01:00 -i input.mp4 -t 00:00:30 -c copy output.mp4

# Accurate seek (slower)
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 output.mp4

# Start to end time
ffmpeg -ss 00:01:00 -i input.mp4 -to 00:01:30 -c copy output.mp4
```

---

## Resize Video

```bash
# Specific resolution
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# Auto height (keep aspect)
ffmpeg -i input.mp4 -vf scale=1280:-1 output.mp4
ffmpeg -i input.mp4 -vf scale=-2:720 output.mp4

# Scale by factor
ffmpeg -i input.mp4 -vf scale=iw/2:ih/2 output.mp4

# Fit within box
ffmpeg -i input.mp4 -vf "scale='min(1280,iw)':'min(720,ih)':force_original_aspect_ratio=decrease" output.mp4
```

---

## Create GIF

```bash
# Basic
ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1" output.gif

# High quality with palette
ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif

# From segment
ffmpeg -ss 00:00:05 -t 3 -i input.mp4 -vf "fps=15,scale=480:-1" output.gif
```

---

## Merge/Concatenate

```bash
# Concat demuxer (same codec)
# filelist.txt: file 'part1.mp4' (one per line)
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# Concat filter (different codecs)
ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" output.mp4
```

---

## Subtitles

```bash
# Burn subtitles (hardcode)
ffmpeg -i input.mp4 -vf subtitles=subs.srt output.mp4

# With custom style
ffmpeg -i input.mp4 -vf "subtitles=subs.srt:force_style='FontSize=24'" output.mp4

# Add subtitle stream (soft)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text output.mp4

# Multiple languages
ffmpeg -i input.mp4 -i english.srt -i spanish.srt \
  -map 0:v -map 0:a -map 1 -map 2 -c copy -c:s mov_text \
  -metadata:s:s:0 language=eng -metadata:s:s:1 language=spa output.mp4

# Extract subtitles
ffmpeg -i input.mkv -map 0:s:0 output.srt
```

---

## Text Overlay (drawtext)

```bash
# Centered text
ffmpeg -i input.mp4 -vf "drawtext=text='Hello':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" output.mp4

# With background box
ffmpeg -i input.mp4 -vf "drawtext=text='Title':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.7" output.mp4

# Timestamp
ffmpeg -i input.mp4 -vf "drawtext=text='%{pts\\:hms}':fontsize=24:fontcolor=white:x=10:y=10" output.mp4

# Frame number
ffmpeg -i input.mp4 -vf "drawtext=text='Frame %{frame_num}':fontsize=24:x=10:y=10" output.mp4

# Timed text (2s to 5s)
ffmpeg -i input.mp4 -vf "drawtext=text='Hi':fontsize=32:enable='between(t,2,5)'" output.mp4
```

### Position Reference
```
x=10              → left
x=w-tw-10         → right
x=(w-text_w)/2    → center

y=10              → top
y=h-th-10         → bottom
y=(h-text_h)/2    → center
```

---

## Extract/Create Frames

```bash
# Single frame at timestamp
ffmpeg -ss 00:00:10 -i input.mp4 -frames:v 1 frame.png

# Frame every second
ffmpeg -i input.mp4 -vf fps=1 frame_%04d.png

# Every 5 seconds
ffmpeg -i input.mp4 -vf fps=1/5 frame_%04d.png

# All frames
ffmpeg -i input.mp4 frames/frame_%06d.png

# Images to video
ffmpeg -framerate 24 -i frame%03d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Slideshow with audio
ffmpeg -framerate 1/5 -i img%03d.png -i audio.mp3 -c:v libx264 -shortest output.mp4
```

---

## Audio Operations

```bash
# Replace audio
ffmpeg -i video.mp4 -i newaudio.mp3 -map 0:v -map 1:a -c copy output.mp4

# Add audio to silent video
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output.mp4

# Mix audio tracks
ffmpeg -i video.mp4 -i music.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" output.mp4

# Volume adjustment
ffmpeg -i input.mp4 -af "volume=1.5" output.mp4
ffmpeg -i input.mp4 -af "volume=10dB" output.mp4

# Normalize
ffmpeg -i input.mp4 -af loudnorm output.mp4
```

---

## Video Transformations

### Rotate/Flip
```bash
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4   # 90° CW
ffmpeg -i input.mp4 -vf "transpose=2" output.mp4   # 90° CCW
ffmpeg -i input.mp4 -vf "hflip" output.mp4         # Horizontal flip
ffmpeg -i input.mp4 -vf "vflip" output.mp4         # Vertical flip
```

### Crop
```bash
ffmpeg -i input.mp4 -vf "crop=640:480:100:50" output.mp4  # w:h:x:y
ffmpeg -i input.mp4 -vf "crop=min(iw\,ih):min(iw\,ih)" output.mp4  # Center square
```

### Overlay/Watermark
```bash
ffmpeg -i video.mp4 -i logo.png -filter_complex "overlay=10:10" output.mp4
ffmpeg -i video.mp4 -i logo.png -filter_complex "overlay=W-w-10:H-h-10" output.mp4  # Bottom-right
```

### Speed
```bash
# 2x speed
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" output.mp4

# 0.5x speed
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" output.mp4
```

### Fade
```bash
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=2" output.mp4
ffmpeg -i input.mp4 -vf "fade=t=out:st=58:d=2" output.mp4
ffmpeg -i input.mp4 -af "afade=t=in:d=2,afade=t=out:st=58:d=2" output.mp4
```

---

## Screen Capture

```bash
# Windows
ffmpeg -f gdigrab -framerate 30 -i desktop output.mp4
ffmpeg -f gdigrab -framerate 30 -i title="Window Title" output.mp4

# Linux X11
ffmpeg -f x11grab -video_size 1920x1080 -framerate 25 -i :0.0 output.mp4

# macOS
ffmpeg -f avfoundation -framerate 30 -i "1" output.mp4
```

---

## Hardware Acceleration

```bash
# NVIDIA NVENC
ffmpeg -i input.mp4 -c:v h264_nvenc -preset fast output.mp4
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4

# Intel QuickSync
ffmpeg -i input.mp4 -c:v h264_qsv output.mp4

# AMD AMF
ffmpeg -i input.mp4 -c:v h264_amf output.mp4

# List available
ffmpeg -hwaccels
```

---

## Information Commands

```bash
ffmpeg -i input.mp4                    # Basic info
ffprobe input.mp4                      # Detailed info
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

ffmpeg -codecs                         # List codecs
ffmpeg -encoders                       # List encoders
ffmpeg -decoders                       # List decoders
ffmpeg -formats                        # List formats
ffmpeg -filters                        # List filters
ffmpeg -pix_fmts                       # List pixel formats
```
