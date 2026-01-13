# FFmpeg Advanced Topics

## Adaptive Streaming (HLS / DASH)

Adaptive streaming creates multiple quality versions divided into chunks for HTTP delivery.

### HLS (HTTP Live Streaming)

```bash
# Multi-quality HLS
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]split=3[v1][v2][v3]; \
    [v1]scale=1920:1080[v1out]; \
    [v2]scale=1280:720[v2out]; \
    [v3]scale=854:480[v3out]" \
  -map "[v1out]" -map 0:a -c:v libx264 -b:v 5M -c:a aac -b:a 192k \
    -hls_time 6 -hls_playlist_type vod -hls_segment_filename "1080p_%03d.ts" 1080p.m3u8 \
  -map "[v2out]" -map 0:a -c:v libx264 -b:v 3M -c:a aac -b:a 128k \
    -hls_time 6 -hls_playlist_type vod -hls_segment_filename "720p_%03d.ts" 720p.m3u8 \
  -map "[v3out]" -map 0:a -c:v libx264 -b:v 1M -c:a aac -b:a 96k \
    -hls_time 6 -hls_playlist_type vod -hls_segment_filename "480p_%03d.ts" 480p.m3u8

# Simple HLS
ffmpeg -i input.mp4 -c:v libx264 -c:a aac \
  -hls_time 10 -hls_list_size 0 -hls_segment_filename "segment_%03d.ts" output.m3u8
```

### HLS Options
| Option | Purpose |
|--------|---------|
| `-hls_time` | Segment duration (seconds) |
| `-hls_list_size` | Max playlist entries (0 = unlimited) |
| `-hls_playlist_type vod` | Video on demand |
| `-hls_playlist_type event` | Live event |
| `-hls_segment_filename` | Segment filename pattern |

### DASH (Dynamic Adaptive Streaming)

```bash
ffmpeg -i input.mp4 \
  -map 0:v -map 0:v -map 0:a \
  -c:v libx264 -c:a aac \
  -b:v:0 5M -s:v:0 1920x1080 \
  -b:v:1 3M -s:v:1 1280x720 \
  -b:a:0 192k \
  -f dash -seg_duration 4 \
  -adaptation_sets "id=0,streams=v id=1,streams=a" \
  output.mpd
```

---

## Fragmented MP4 (fMP4)

Standard MP4 stores metadata at start/end. Fragmented MP4 enables streaming.

```bash
# Create fragmented MP4
ffmpeg -i input.mp4 -c copy -movflags frag_keyframe+empty_moov output_frag.mp4

# For DASH
ffmpeg -i input.mp4 -c copy -movflags frag_keyframe+empty_moov+default_base_moof output.mp4

# Optimize for web (move moov to start)
ffmpeg -i input.mp4 -c copy -movflags +faststart output.mp4
```

### movflags
| Flag | Purpose |
|------|---------|
| `frag_keyframe` | Fragment at keyframes |
| `empty_moov` | Empty moov atom (streaming) |
| `faststart` | Moov at start (web download) |

---

## RTMP Streaming

```bash
# Stream to Twitch/YouTube
ffmpeg -re -i input.mp4 -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k \
  -c:a aac -b:a 160k -ar 44100 \
  -f flv rtmp://live.twitch.tv/app/YOUR_STREAM_KEY

# Webcam streaming
ffmpeg -f dshow -i video="Webcam":audio="Microphone" \
  -c:v libx264 -preset veryfast -b:v 2500k \
  -c:a aac -b:a 128k \
  -f flv rtmp://server/live/stream

# Re-stream
ffmpeg -i rtmp://source/live/stream -c copy -f flv rtmp://destination/live/stream
```

---

## Complex Filtergraphs

Use `-filter_complex` for multiple inputs/outputs.

### Syntax
```
[input_label]filter=params[output_label];[input_label]filter[output_label]
```

### Picture-in-Picture
```bash
ffmpeg -i main.mp4 -i overlay.mp4 \
  -filter_complex "[1:v]scale=320:180[pip];[0:v][pip]overlay=W-w-10:10[out]" \
  -map "[out]" -map 0:a output.mp4
```

### Side-by-Side
```bash
ffmpeg -i left.mp4 -i right.mp4 \
  -filter_complex "[0:v][1:v]hstack=inputs=2[v]" \
  -map "[v]" output.mp4
```

### Vertical Stack
```bash
ffmpeg -i top.mp4 -i bottom.mp4 \
  -filter_complex "[0:v][1:v]vstack=inputs=2[v]" \
  -map "[v]" output.mp4
```

### 2x2 Grid
```bash
ffmpeg -i 1.mp4 -i 2.mp4 -i 3.mp4 -i 4.mp4 \
  -filter_complex "[0:v][1:v]hstack[top];[2:v][3:v]hstack[bottom];[top][bottom]vstack[v]" \
  -map "[v]" output.mp4
```

### Crossfade Between Videos
```bash
ffmpeg -i first.mp4 -i second.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=4[v];[0:a][1:a]acrossfade=d=1[a]" \
  -map "[v]" -map "[a]" output.mp4
```

### xfade Transitions
`fade`, `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `slideleft`, `slideright`, `circlecrop`, `rectcrop`, `fadeblack`, `fadewhite`, `radial`, `circleopen`, `circleclose`, `dissolve`, `pixelize`, `diagtl`, `diagtr`, `diagbl`, `diagbr`

### Mix Audio Tracks
```bash
ffmpeg -i video.mp4 -i music.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]" \
  -map 0:v -map "[a]" output.mp4
```

---

## Batch Processing

### Windows (PowerShell)
```powershell
# Convert all MP4 to MKV
Get-ChildItem *.mp4 | ForEach-Object { ffmpeg -i $_.Name -c copy ($_.BaseName + ".mkv") }

# Compress all videos
Get-ChildItem *.mp4 | ForEach-Object { ffmpeg -i $_.Name -c:v libx264 -crf 23 ("compressed_" + $_.Name) }

# Extract audio from all
Get-ChildItem *.mp4 | ForEach-Object { ffmpeg -i $_.Name -vn -c:a libmp3lame ($_.BaseName + ".mp3") }
```

### Linux/macOS (Bash)
```bash
# Convert all MP4 to MKV
for f in *.mp4; do ffmpeg -i "$f" -c copy "${f%.mp4}.mkv"; done

# Compress all videos
for f in *.mp4; do ffmpeg -i "$f" -c:v libx264 -crf 23 "compressed_$f"; done

# Extract audio from all
for f in *.mp4; do ffmpeg -i "$f" -vn -c:a libmp3lame "${f%.mp4}.mp3"; done

# Resize all images
for f in *.png; do ffmpeg -i "$f" -vf scale=800:-1 "resized_$f"; done
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Audio/video out of sync | Use `-async 1` or `-vsync cfr` |
| "Non-monotonous DTS" | Add `-fflags +genpts` before `-i` |
| Green/corrupted frames | Add `-vsync drop` or re-encode |
| File won't play | Use `-movflags +faststart` for MP4 |
| Seek doesn't work | Ensure keyframes exist, re-encode |
| Aspect ratio wrong | Use `-aspect 16:9` or check SAR/DAR |
| No audio after merge | Check `-map` options |
| Subtitle burn fails | Ensure subtitle file path has no spaces |

### Debug Commands

```bash
# Show all stream info
ffprobe -show_streams input.mp4

# Show packets (timing)
ffprobe -show_packets input.mp4

# Show frames
ffprobe -show_frames input.mp4

# Verbose encoding
ffmpeg -v debug -i input.mp4 output.mp4

# Test filter without encoding
ffplay -vf "scale=640:-1" input.mp4
```

### Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `Avi header missing` | Corrupted file | Try `-ignore_unknown` |
| `moov atom not found` | Incomplete download | Re-download file |
| `Invalid data` | Codec mismatch | Specify correct codec |
| `Permission denied` | File in use | Close other apps |
| `No such filter` | Filter not compiled | Check `ffmpeg -filters` |

---

## Performance Tips

1. **Use `-c copy`** when possible (10-100x faster)
2. **Hardware acceleration** for encoding (NVENC, QSV, AMF)
3. **Faster presets** for live encoding (`-preset ultrafast`)
4. **Limit threads** if needed: `-threads 4`
5. **Avoid filters** when not needed
6. **Use `-ss` before `-i`** for faster seeking
7. **Two-pass** only when file size matters more than speed
