# Kimi CLI Integration - Overview

**Created:** 2026-01-28
**Branch:** `feature/kimi-cli-integration`
**Status:** Planning
**Estimated Effort:** 2-3 weeks (split into phases)

---

## Goal

Integrate [MoonshotAI/kimi-cli](https://github.com/MoonshotAI/kimi-cli) into the AI Content Pipeline to enable:
1. AI-powered pipeline generation from natural language
2. Code analysis and refactoring assistance
3. Interactive debugging capabilities
4. Multi-agent workflows combining Kimi with existing models

---

## Implementation Phases

| Phase | Description | Status | Issue File |
|-------|-------------|--------|------------|
| 1 | Add Submodule & SDK Setup | Pending | `01-submodule-setup.md` |
| 2 | Create Integration Wrapper | Pending | `02-integration-wrapper.md` |
| 3 | CLI Commands & Pipeline Support | Pending | `03-cli-pipeline-support.md` |
| 4 | Natural Language Pipeline Generation | Pending | `04-nl-pipeline-generation.md` |
| 5 | Testing & Documentation | Pending | `05-testing-documentation.md` |

---

## Key Differences: Current Package vs Kimi CLI

| Aspect | AI Content Pipeline | Kimi CLI | Action Needed |
|--------|---------------------|----------|---------------|
| Python Version | 3.8+ | 3.12+ | Consider compatibility layer |
| Package Manager | pip | uv | Support both |
| CLI Framework | Click | Typer | Keep Click, call Kimi SDK |
| Async | Sync-first | Async-native | Add async wrappers |
| Config Format | YAML | JSON (MCP) | Bridge configuration |

---

## Architecture Decision

**Approach: SDK Integration (not full CLI embedding)**

Reasons:
1. Avoid Python version conflicts
2. Use only what we need (SDK)
3. Maintain our CLI patterns (Click)
4. Easier maintenance and updates

```
ai-content-pipeline/
├── packages/
│   └── external/
│       └── kimi-cli/              # Git submodule (reference only)
│           └── sdks/kimi-sdk/     # SDK we'll use
├── ai_content_pipeline/
│   └── integrations/
│       └── kimi/                  # Our integration layer
│           ├── __init__.py
│           ├── client.py          # Kimi SDK wrapper
│           ├── pipeline_generator.py
│           └── tools.py           # Custom tools for Kimi
```

---

## Dependencies to Add

```txt
# requirements.txt additions
kimi-sdk>=1.2.0
aiohttp>=3.9.0
```

---

## Environment Variables

```bash
# .env additions
KIMI_API_KEY=your_kimi_api_key
KIMI_BASE_URL=https://api.moonshot.cn  # Optional
```

---

## Success Criteria

- [ ] Kimi SDK installed and functional
- [ ] Integration wrapper with sync/async support
- [ ] CLI command: `aicp generate-pipeline --prompt "..."`
- [ ] YAML step type: `type: "kimi_agent"`
- [ ] Unit tests passing
- [ ] Documentation updated

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python 3.12 requirement | High | Use SDK only, not full CLI |
| API rate limits | Medium | Add retry/backoff logic |
| Dependency conflicts | Medium | Isolate in integration module |
| Breaking API changes | Low | Pin SDK version |

---

## References

- [Kimi CLI Repository](https://github.com/MoonshotAI/kimi-cli)
- [Kimi SDK Documentation](https://github.com/MoonshotAI/kimi-cli/tree/main/sdks/kimi-sdk)
- [Integration Guide](../docs/KIMI_CLI_INTEGRATION.md)
