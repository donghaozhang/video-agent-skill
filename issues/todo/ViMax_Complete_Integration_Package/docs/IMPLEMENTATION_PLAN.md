# ViMax Integration - Implementation Plan

## Overview

This document provides a structured implementation plan for integrating ViMax features into the video-agent-skill (ai-content-pipeline) project. The plan is divided into phases with detailed subtasks, file paths, and test specifications.

**Total Estimated Effort**: 10-16 days
**Approach**: Long-term maintainability over quick fixes

---

## Implementation Phases

| Phase | Description | Subtask Files |
|-------|-------------|---------------|
| Phase 1 | Infrastructure & Directory Setup | [PHASE_1_INFRASTRUCTURE.md](./PHASE_1_INFRASTRUCTURE.md) |
| Phase 2 | Adapter Layer Implementation | [PHASE_2_ADAPTERS.md](./PHASE_2_ADAPTERS.md) |
| Phase 3 | Agent Migration | [PHASE_3_AGENTS.md](./PHASE_3_AGENTS.md) |
| Phase 4 | Pipeline Integration | [PHASE_4_PIPELINES.md](./PHASE_4_PIPELINES.md) |
| Phase 5 | CLI Commands & Testing | [PHASE_5_CLI_TESTING.md](./PHASE_5_CLI_TESTING.md) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                 │
│  ai-content-pipeline vimax-* commands                           │
├─────────────────────────────────────────────────────────────────┤
│                     Pipeline Layer                               │
│  Idea2VideoPipeline | Script2VideoPipeline | Novel2MoviePipeline│
├─────────────────────────────────────────────────────────────────┤
│                      Agent Layer                                 │
│  Screenwriter | StoryboardArtist | CharacterExtractor | ...     │
├─────────────────────────────────────────────────────────────────┤
│                     Adapter Layer                                │
│  ImageGeneratorAdapter | VideoGeneratorAdapter | LLMAdapter     │
├─────────────────────────────────────────────────────────────────┤
│                    Generator Layer                               │
│  FAL | Replicate | Google Veo | OpenRouter | ElevenLabs        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key File Locations

### Existing Codebase (video-agent-skill)

```
packages/core/ai_content_platform/
├── cli/main.py                          # CLI entry point
├── core/
│   ├── models.py                        # Pydantic models
│   ├── registry.py                      # Step registry
│   └── executor.py                      # Pipeline executor
└── ai_content_pipeline/
    └── pipeline/
        ├── step_executors/
        │   ├── base.py                  # BaseStepExecutor
        │   ├── image_steps.py           # Image executors
        │   └── video_steps.py           # Video executors
        ├── chain.py                     # Pipeline chain
        └── executor.py                  # Pipeline executor
```

### ViMax Source (to integrate)

```
issues/todo/ViMax_Complete_Integration_Package/src/
├── agents/                              # LLM-based agents
├── interfaces/                          # Data models
├── pipelines/                           # Pipeline orchestration
├── configs/                             # YAML configs
└── utils/                               # Utilities
```

### New Files to Create

```
packages/core/ai_content_platform/
├── vimax/                               # NEW: ViMax integration module
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── image_adapter.py
│   │   ├── video_adapter.py
│   │   └── llm_adapter.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── character_extractor.py
│   │   ├── character_portraits.py
│   │   ├── reference_selector.py
│   │   ├── screenwriter.py
│   │   ├── storyboard_artist.py
│   │   └── camera_generator.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── character.py
│   │   ├── shot.py
│   │   ├── camera.py
│   │   └── output.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── idea2video.py
│   │   ├── script2video.py
│   │   └── novel2movie.py
│   └── cli/
│       ├── __init__.py
│       └── commands.py
tests/
├── unit/
│   └── vimax/
│       ├── test_adapters.py
│       ├── test_agents.py
│       └── test_pipelines.py
└── integration/
    └── test_vimax_e2e.py
```

---

## Dependencies to Add

Add to `requirements.txt`:

```
# ViMax Integration Dependencies
litellm>=1.0                    # Unified LLM interface
langchain-core>=0.1.0           # Agent framework (optional)
scenedetect[opencv]>=0.6        # Scene detection
tenacity>=8.0                   # Retry logic
```

---

## Quick Reference: Subtask Breakdown

### Phase 1: Infrastructure (1-2 days)
- [ ] 1.1 Create directory structure
- [ ] 1.2 Copy and adapt interfaces
- [ ] 1.3 Add dependencies
- [ ] 1.4 Create base classes

### Phase 2: Adapters (2-3 days)
- [ ] 2.1 ImageGeneratorAdapter
- [ ] 2.2 VideoGeneratorAdapter
- [ ] 2.3 LLMAdapter
- [ ] 2.4 Adapter tests

### Phase 3: Agents (3-5 days)
- [ ] 3.1 CharacterExtractor
- [ ] 3.2 CharacterPortraitsGenerator
- [ ] 3.3 ReferenceImageSelector
- [ ] 3.4 Screenwriter
- [ ] 3.5 StoryboardArtist
- [ ] 3.6 CameraImageGenerator
- [ ] 3.7 Agent tests

### Phase 4: Pipelines (2-3 days)
- [ ] 4.1 Idea2VideoPipeline
- [ ] 4.2 Script2VideoPipeline
- [ ] 4.3 Novel2MoviePipeline
- [ ] 4.4 Pipeline tests

### Phase 5: CLI & Testing (2-3 days)
- [ ] 5.1 CLI commands
- [ ] 5.2 Integration tests
- [ ] 5.3 Documentation
- [ ] 5.4 Example configs

---

## Success Criteria

1. **All ViMax agents work** with existing generators
2. **CLI commands** available for all pipelines
3. **90%+ test coverage** for new code
4. **Documentation** complete with examples
5. **No breaking changes** to existing functionality

---

## Related Documents

- [ViMax_Integration_Plan.md](./ViMax_Integration_Plan.md) - Original integration plan
- [ViMax_Architecture_Details.md](./ViMax_Architecture_Details.md) - Architecture details
- [User_Guide.md](./User_Guide.md) - User guide
- [Feature_Comparison_Analysis.md](./Feature_Comparison_Analysis.md) - Feature comparison

---

*Document Version: 1.0*
*Created: 2026-02-03*
*Author: AI Assistant*
