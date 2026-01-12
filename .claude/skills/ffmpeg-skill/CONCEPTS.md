# FFmpeg Core Concepts

## Video
A sequence of images (frames) displayed at a specific rate.

| Frame Rate | Use Case |
|------------|----------|
| 24 fps | Cinema/film |
| 25 fps | TV (PAL) |
| 30 fps | TV/web (NTSC) |
| 60 fps | Gaming/smooth motion |

Raw 1080p at 24fps for 30 minutes = ~250GB uncompressed. Codecs make this practical.

---

## Audio
Sound waves digitized via Analog-to-Digital Conversion (ADC).

| Parameter | Common Values |
|-----------|---------------|
| Sample Rate | 44100 Hz (CD), 48000 Hz (video) |
| Bit Depth | 16-bit, 24-bit |
| Channels | Mono (1), Stereo (2), 5.1 (6), 7.1 (8) |

---

## Codec (Coder-Decoder)
Compresses/decompresses media data.

### Video Codecs
| Codec | Description |
|-------|-------------|
| H.264/AVC | Most compatible, good quality |
| H.265/HEVC | 50% smaller than H.264, slower encode |
| VP9 | Google's open codec, WebM |
| AV1 | Newest, best compression, slow encode |

### Audio Codecs
| Codec | Description |
|-------|-------------|
| AAC | Standard for MP4, good quality |
| MP3 | Legacy, universal support |
| Opus | Best quality at low bitrates |
| FLAC | Lossless compression |

---

## Container (Format)
Wrapper holding compressed streams + metadata. **Container ≠ Codec!**

| Extension | Container | Typical Codecs |
|-----------|-----------|----------------|
| .mp4 | MPEG-4 Part 14 | H.264/H.265 + AAC |
| .mkv | Matroska | Any codec, very flexible |
| .webm | WebM | VP8/VP9 + Vorbis/Opus |
| .avi | AVI | Legacy, limited |
| .mov | QuickTime | H.264 + AAC |
| .ts | MPEG-TS | H.264 + AAC (streaming) |

---

## FFmpeg Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  INPUT      │    │  DEMUX      │    │  DECODE     │    │  FILTER     │    │  ENCODE     │
│  Protocol   │───▶│  Extract    │───▶│  Decompress │───▶│  Transform  │───▶│  Compress   │
│  file/http  │    │  Streams    │    │  to Raw     │    │  (optional) │    │  (optional) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                                    │
                                                                                    ▼
                                                         ┌─────────────┐    ┌─────────────┐
                                                         │  OUTPUT     │◀───│  MUX        │
                                                         │  Protocol   │    │  Combine    │
                                                         │  file/http  │    │  Streams    │
                                                         └─────────────┘    └─────────────┘
```

---

## Processing Modes

| Mode | Description | Command | Use Case |
|------|-------------|---------|----------|
| **Transmuxing** | Change container only | `-c copy` | MP4 → MKV (fast) |
| **Transcoding** | Change codec | `-c:v libx264` | H.265 → H.264 |
| **Transrating** | Change bitrate | `-b:v 1M` | Reduce file size |
| **Transsizing** | Change resolution | `-vf scale=1280:720` | 4K → 1080p |

```bash
# Transmuxing (fast, no re-encode)
ffmpeg -i input.mp4 -c copy output.ts

# Transcoding (codec change)
ffmpeg -i input.mp4 -c:v libx265 output.mp4

# Transrating (bitrate change)
ffmpeg -i input.mp4 -b:v 1M -b:a 128k output.mp4

# Transsizing (resolution change)
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
```

---

## Timing & Synchronization

### Timestamps
| Term | Meaning |
|------|---------|
| **PTS** (Presentation Timestamp) | When frame should be displayed |
| **DTS** (Decoding Timestamp) | When frame should be decoded |
| **Timebase** | Unit of time measurement (e.g., 1/90000) |

DTS ≠ PTS when B-frames are used (frames decoded out of display order).

### Fix Timestamp Issues
```bash
# Reset timestamps (fix sync issues)
ffmpeg -i input.mp4 -fflags +genpts -c copy output.mp4

# Force constant frame rate
ffmpeg -i input.mp4 -vsync cfr -r 30 output.mp4

# Copy timestamps from source
ffmpeg -i input.mp4 -copyts -c copy output.mp4
```

---

## Quality Settings

### CRF (Constant Rate Factor) for x264/x265
| CRF | Quality | Use Case |
|-----|---------|----------|
| 0 | Lossless | Archival |
| 17-18 | Visually lossless | High quality |
| 19-23 | High quality | Default (23) |
| 24-28 | Medium quality | Web/streaming |
| 29-51 | Low quality | Small file size |

### Presets (Speed vs Compression)
| Preset | Speed | File Size |
|--------|-------|-----------|
| ultrafast | Fastest | Largest |
| veryfast | | |
| fast | | |
| medium | Default | |
| slow | | |
| veryslow | Slowest | Smallest |

```bash
# Fast encode, larger file
ffmpeg -i input.mp4 -c:v libx264 -preset ultrafast -crf 23 output.mp4

# Slow encode, smaller file
ffmpeg -i input.mp4 -c:v libx264 -preset veryslow -crf 23 output.mp4
```
