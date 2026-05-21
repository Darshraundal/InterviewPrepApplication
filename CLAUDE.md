# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal .NET interview preparation portal — an ASP.NET Core 8.0 MVC application with a dark-themed UI. It serves interview questions (categorized and project-specific) and tracks per-user progress, custom answers, notes, and favorites.

## Commands

All commands run from `src/InterviewPrepPortal/`:

```powershell
# Run the app (auto-migrates DB on startup)
dotnet run

# Build
dotnet build

# Add an EF Core migration
dotnet ef migrations add <MigrationName>

# Apply migrations manually (normally happens automatically at startup)
dotnet ef database update
```

The app runs at `https://localhost:7265` / `http://localhost:5202` in development.

## Architecture

### Dual Data Layer — the central design decision

**Static content (questions, categories, project guides)** lives in JSON files under `Data/JsonData/`. These are never written to at runtime. Three **Singleton** services load them once at startup and cache in `IMemoryCache` with a 24-hour sliding expiration:

- `QuestionService` — reads `categories.json` and all `questions-{slug}.json` files
- `ProjectGuideService` — reads `projects/projects-index.json` and each project's data file referenced by `dataFile` field
- `SearchService` — delegates to the two services above, does no I/O itself

**User data (progress, notes, custom answers, favorites)** lives in SQLite via EF Core. Three **Scoped** services access it:

- `ProgressService` — upserts `UserProgress` rows (status, confidence, revision flag, favorite flag)
- `CustomAnswerService` — user's own answer text per question
- `NoteService` — freeform notes per question

The SQLite database file (`interviewprep.db`) is auto-created and migrated at startup via `db.Database.Migrate()` in `Program.cs`.

### Question ID conventions

- Category question IDs: `{category-prefix}-{number}` e.g., `di-001`, `efcore-003`
- Project question IDs: `{project-slug}-{number}` e.g., `foliotrack-dotnet-001`
- `QuestionSource` discriminator string: `"category"` or `"project"`
- The `(UserId, QuestionId, QuestionSource)` triple is the unique key for all user data tables

### Adding new question categories

1. Add the category entry to `Data/JsonData/categories.json`
2. Create `Data/JsonData/questions-{slug}.json` following the `QuestionsFile` schema (`categoryId` + `questions[]`)
3. The `QuestionService` automatically discovers any file matching `questions-*.json`

### Adding new project guides

1. Add project metadata to `Data/JsonData/projects/projects-index.json` with a `dataFile` path
2. Create the project detail JSON file at that path following the `ProjectDetail` schema
3. `ProjectGuideService` loads it from the index on next startup/cache miss

### MVC structure

Controllers in `Controllers/` are all `[Authorize]` by default. AJAX endpoints (progress updates, note saves, answer saves) return `Json(new { success, message })`. Views use strongly-typed ViewModels from `ViewModels/{Feature}/`.

The layout (`Views/Shared/_Layout.cshtml`) injects `IQuestionService` and `IProgressService` directly to populate the sidebar — be aware that layout code runs on every page and hits the cached singletons.

### EF Core models (`Models/`)

- `ApplicationUser` extends `IdentityUser` with `DisplayName`, `RegisteredAt`, `LastLoginAt`
- `UserProgress`, `UserCustomAnswer`, `UserNote`, `UserFavorite` — all keyed by `(UserId, QuestionId, QuestionSource)` with a unique index enforced in `ApplicationDbContext.OnModelCreating`

### JSON content models (`JsonModels/`)

These are deserialization-only POCOs. `Question` has optional `ProjectExample`, `FollowUps`, `Tags`, and `CrossReferenceIds`. `ProjectGuide` is the index entry; `ProjectDetail` contains the full data including `ArchitectureSummary` and `ProjectSection[]`.
