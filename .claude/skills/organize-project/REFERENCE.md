# QCut Project Organization Reference

## Complete Folder Structure

### Root Level
```
{ProjectName}/
├── project.qcut          # JSON project metadata
├── media/                # All media assets
├── skills/               # Claude Code skills
├── output/               # Final exports
├── cache/                # Processing cache
└── docs/                 # Optional documentation
```

### Media Folder Details
```
media/
├── imported/             # User-imported files
│   ├── video/            # Optional: organize by type
│   ├── audio/
│   └── images/
├── generated/            # AI-generated content
│   ├── images/           # Generated images
│   ├── videos/           # Generated videos
│   └── audio/            # Generated audio/speech
└── temp/                 # Processing intermediates
    └── frames/           # Extracted frames for analysis
```

### Skills Folder Details
```
skills/
├── ai-content-pipeline/
│   ├── Skill.md          # Main skill instructions
│   ├── REFERENCE.md      # API and model reference
│   └── EXAMPLES.md       # Usage examples
├── ffmpeg-skill/
│   ├── Skill.md
│   ├── REFERENCE.md
│   ├── CONCEPTS.md
│   └── ADVANCED.md
└── custom-skill/         # User-created skills
    └── Skill.md
```

## File Type Mappings

| Extension | Category | Destination |
|-----------|----------|-------------|
| .mp4, .mov, .webm, .avi, .mkv | Video | media/imported/ or media/generated/ |
| .jpg, .jpeg, .png, .webp, .gif, .bmp | Image | media/imported/ or media/generated/ |
| .mp3, .wav, .aac, .m4a, .flac, .ogg | Audio | media/imported/ or media/generated/ |
| .srt, .vtt, .ass | Subtitle | media/imported/ |
| .json, .yaml, .yml | Config | project root or docs/ |
| .md | Documentation | docs/ or skills/ |

## Virtual Folder System

### MediaFolder Interface
```typescript
interface MediaFolder {
  id: string;              // Unique identifier
  name: string;            // Display name (max 50 chars)
  parentId: string | null; // null = root level
  color?: string;          // Hex color (e.g., "#ef4444")
  isExpanded: boolean;     // UI collapse state
  createdAt: number;       // Timestamp
  updatedAt: number;       // Timestamp
}
```

### MediaItem Folder Assignment
```typescript
interface MediaItem {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'image';
  folderIds?: string[];       // Can be in multiple folders
  localPath?: string;         // Path on disk
  importMetadata?: MediaImportMetadata;  // Import tracking
  // ... other fields
}
```

### Media Import Metadata
```typescript
interface MediaImportMetadata {
  importMethod: 'symlink' | 'copy';  // How file was imported
  originalPath: string;               // Original file location
  importedAt: number;                 // Timestamp of import
  fileSize: number;                   // File size in bytes
}
```

### Folder Constraints
- Maximum depth: 3 levels
- Name length: 1-50 characters
- No duplicate names at same level (recommended)

### Special System Folders
| Folder ID | Purpose |
|-----------|---------|
| `null` | "All Media" view |
| `system-skills-folder` | Skills virtual folder |

## Storage Locations

### IndexedDB Databases (per project)
- `qcut-media-{projectId}` - Media items
- `qcut-media-{projectId}-folders` - Virtual folders

### Electron IPC Paths
```typescript
// Project media path (symlinks/copies)
Documents/QCut/Projects/{projectId}/media/imported/

// Project skills path
Documents/QCut/Projects/{projectId}/skills/

// Global skills path
~/.claude/skills/

// Bundled skills (in app)
{app}/resources/default-skills/
```

### Media Import IPC API
```typescript
// Available via window.electronAPI.mediaImport
interface MediaImportAPI {
  // Import media with symlink preference, copy fallback
  import(options: {
    sourcePath: string;
    projectId: string;
    mediaId: string;
    preferSymlink?: boolean;
  }): Promise<MediaImportResult>;

  // Validate symlink target exists
  validateSymlink(path: string): Promise<boolean>;

  // Get original path from symlink
  locateOriginal(mediaPath: string): Promise<string | null>;

  // Re-link to new source location
  relinkMedia(projectId: string, mediaId: string, newSourcePath: string): Promise<MediaImportResult>;

  // Remove imported file (symlink or copy)
  remove(projectId: string, mediaId: string): Promise<void>;

  // Check if system supports symlinks
  checkSymlinkSupport(): Promise<boolean>;

  // Get media folder path for project
  getMediaPath(projectId: string): Promise<string>;
}

interface MediaImportResult {
  success: boolean;
  targetPath: string;
  importMethod: 'symlink' | 'copy';
  originalPath: string;
  fileSize: number;
  error?: string;
}
```

## Best Practices

### Naming Conventions
- Use lowercase with hyphens for folders: `raw-footage`, `sound-effects`
- Use descriptive names for files: `interview-john-2024-01-15.mp4`
- Avoid special characters: `< > : " / \ | ? *`

### Organization Workflow
1. **Import** - Files added to `media/imported/`
2. **Organize** - Assign to virtual folders in UI
3. **Process** - Temp files created in `media/temp/`
4. **Generate** - AI content saved to `media/generated/`
5. **Export** - Final render to `output/`
6. **Cleanup** - Remove temp files, clear cache

### When NOT to Move Files
- Files already referenced in timeline
- Files with external dependencies
- System-generated cache files
- Files in use by FFmpeg

## Common Issues

### Broken References
If files are moved manually:
1. Check project.qcut for hardcoded paths
2. Update media item localPath in IndexedDB
3. Re-import if necessary

### Broken Symlinks
If original files are moved/deleted:
1. Find broken symlinks: `find media/imported -xtype l`
2. Use `window.electronAPI.mediaImport.locateOriginal()` to check target
3. Re-link using `relinkMedia()` with new source path
4. Or re-import the file entirely

### Symlinks Not Working (Windows)
Symlink creation requires either:
- **Administrator privileges**: Run app as admin
- **Developer Mode**: Enable in Windows Settings → Privacy & Security → For developers
- If neither available, QCut automatically falls back to copying files

### Duplicate Files
To find duplicates:
```bash
# Find by name
find . -type f -name "*.mp4" | xargs -I {} basename {} | sort | uniq -d

# Find by size (potential duplicates)
find . -type f -printf "%s %p\n" | sort -n | uniq -D -w 15
```

### Large Projects
For projects > 1GB:
- Use external storage for raw footage
- Keep only working files in project folder
- Archive completed projects
