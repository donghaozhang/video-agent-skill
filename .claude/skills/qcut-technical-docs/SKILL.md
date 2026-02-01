---
name: qcut-technical-docs
description: QCut technical documentation and architecture reference. Use when understanding codebase structure, AI video workflows, testing infrastructure, terminal system, or finding specific implementation details.
user-invocable: false
---

# QCut Technical Documentation

Reference documentation for QCut's architecture, workflows, and implementation details.

## Documentation Index

For full navigation, see [docs/technical/README.md](../../../docs/technical/README.md).

## Quick Reference

### Architecture
| Topic | File | Use When |
|-------|------|----------|
| Source Code Structure | [architecture/source-code-structure.md](../../../docs/technical/architecture/source-code-structure.md) | Finding files, understanding folder layout |
| Terminal Architecture | [architecture/terminal-architecture.md](../../../docs/technical/architecture/terminal-architecture.md) | Understanding xterm.js integration |
| Virtual Folder System | [architecture/virtual-folder-system.md](../../../docs/technical/architecture/virtual-folder-system.md) | Media organization, folder metadata |

### AI Video Generation
| Topic | File | Use When |
|-------|------|----------|
| AI Workflow | [ai/workflow.md](../../../docs/technical/ai/workflow.md) | Working with AI video generation, FAL.ai |
| Skills System | [ai/skills-system.md](../../../docs/technical/ai/skills-system.md) | How skills work in QCut |

### AI Models
| Category | Folder | Models |
|----------|--------|--------|
| Text-to-Video | [ai/models/text-to-video/](../../../docs/technical/ai/models/text-to-video/) | Sora 2, Veo 3, Kling, MiniMax, Wan, LTX |
| Image-to-Video | [ai/models/image-to-video/](../../../docs/technical/ai/models/image-to-video/) | Runway Gen-3, Kling, Luma, Veo 2 |
| Avatar | [ai/models/avatar/](../../../docs/technical/ai/models/avatar/) | Hedra, Sync, Hailuo |
| Transcription | [ai/models/transcription/](../../../docs/technical/ai/models/transcription/) | ElevenLabs Scribe, Whisper |
| Text-to-Image | [ai/models/text-to-image/](../../../docs/technical/ai/models/text-to-image/) | Flux, SDXL, Ideogram |
| Image Upscale | [ai/models/image-upscale/](../../../docs/technical/ai/models/image-upscale/) | Real-ESRGAN, Clarity |
| Segmentation | [ai/models/segmentation/](../../../docs/technical/ai/models/segmentation/) | SAM, BiRefNet |
| Adjustment Panel | [ai/models/adjustment-panel/](../../../docs/technical/ai/models/adjustment-panel/) | Color grading, filters |

### Testing
| Topic | File | Use When |
|-------|------|----------|
| Test Infrastructure | [testing/infrastructure.md](../../../docs/technical/testing/infrastructure.md) | Writing tests, understanding test setup |
| E2E Testing | [testing/e2e.md](../../../docs/technical/testing/e2e.md) | End-to-end testing with Playwright |

### Workflows
| Topic | File | Use When |
|-------|------|----------|
| Effects Workflow | [workflows/effects-sequence.md](../../../docs/technical/workflows/effects-sequence.md) | Video effects pipeline |
| Drawing Canvas | [workflows/drawing-canvas-sequence.md](../../../docs/technical/workflows/drawing-canvas-sequence.md) | Canvas drawing implementation |

### Guides
| Topic | File | Use When |
|-------|------|----------|
| Build Commands | [guides/build-commands.md](../../../docs/technical/guides/build-commands.md) | Building, running, deploying |

## Architecture Overview

### Tech Stack
- **Frontend**: Vite 7.0.6 + TanStack Router + React 18.3.1
- **Desktop**: Electron 37.4.0 (100% TypeScript)
- **State**: Zustand stores
- **Video**: FFmpeg WebAssembly
- **AI**: FAL.ai (40+ models)
- **Testing**: Vitest 3.2.4 (200+ tests)

### Key Directories
```
apps/web/src/
├── routes/          # TanStack Router pages
├── components/      # React components
│   ├── ui/          # Radix UI primitives (73 files)
│   └── editor/      # Video editor components
├── stores/          # Zustand state stores
├── hooks/           # Custom React hooks
├── lib/             # Utilities and services
│   └── ai-video/    # AI video generation
└── types/           # TypeScript definitions

electron/
├── main.ts          # Electron main process
├── preload.ts       # IPC bridge
└── *-handler.ts     # IPC handlers (38 total)
```

## How Claude Uses This Skill

This skill is **model-invoked only** (`user-invocable: false`). Claude automatically loads relevant sections when:

1. **Understanding code structure** → Loads architecture/source-code-structure.md
2. **Working with AI video** → Loads ai/workflow.md + model docs
3. **Writing/debugging tests** → Loads testing/*.md
4. **Terminal features** → Loads architecture/terminal-architecture.md
5. **Build/deploy questions** → Loads guides/build-commands.md
