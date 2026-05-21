using InterviewPrepPortal.Data;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using Microsoft.EntityFrameworkCore;

namespace InterviewPrepPortal.Services;

/// <summary>
/// Scoped service — manages user progress via EF Core + SQLite.
/// </summary>
public class ProgressService(ApplicationDbContext db) : IProgressService
{
    public async Task<UserProgress?> GetProgressAsync(string userId, string questionId, string source)
    {
        return await db.UserProgresses
            .FirstOrDefaultAsync(p =>
                p.UserId == userId &&
                p.QuestionId == questionId &&
                p.QuestionSource == source);
    }

    public async Task<IReadOnlyList<UserProgress>> GetAllProgressAsync(string userId)
    {
        return await db.UserProgresses
            .Where(p => p.UserId == userId)
            .ToListAsync();
    }

    public async Task<ProgressSummary> GetProgressSummaryAsync(string userId)
    {
        var all = await db.UserProgresses.Where(p => p.UserId == userId).ToListAsync();

        var mastered = all.Count(p => p.Status == ProgressStatus.Mastered);
        var learning = all.Count(p => p.Status == ProgressStatus.Learning);
        var notStarted = all.Count(p => p.Status == ProgressStatus.NotStarted);
        var revisionNeeded = all.Count(p => p.IsRevisionNeeded);
        var favorites = all.Count(p => p.IsFavorite);

        var categoryQ = all.Count(p => p.QuestionSource == "category");
        var projectQ = all.Count(p => p.QuestionSource == "project");

        var total = all.Count;
        var pct = total > 0 ? Math.Round((double)mastered / total * 100, 1) : 0;

        return new ProgressSummary(categoryQ, projectQ, mastered, learning, notStarted, pct, revisionNeeded, favorites);
    }

    public async Task<CategoryProgressSummary> GetCategoryProgressAsync(string userId, string categoryId)
    {
        // We can only count what the user has interacted with
        var records = await db.UserProgresses
            .Where(p => p.UserId == userId && p.QuestionSource == "category" && p.QuestionId.StartsWith(categoryId + "-"))
            .ToListAsync();

        return new CategoryProgressSummary(
            categoryId,
            records.Count,
            records.Count(p => p.Status == ProgressStatus.Mastered),
            records.Count(p => p.Status == ProgressStatus.Learning),
            records.Count(p => p.Status == ProgressStatus.NotStarted));
    }

    public async Task<UserProgress> UpsertProgressAsync(string userId, string questionId, string source,
        ProgressStatus status, ConfidenceLevel confidence, bool revisionNeeded, bool isFavorite)
    {
        var existing = await GetProgressAsync(userId, questionId, source);

        if (existing != null)
        {
            existing.Status = status;
            existing.Confidence = confidence;
            existing.IsRevisionNeeded = revisionNeeded;
            existing.IsFavorite = isFavorite;
            existing.LastReviewedAt = DateTime.UtcNow;
            existing.UpdatedAt = DateTime.UtcNow;
        }
        else
        {
            existing = new UserProgress
            {
                UserId = userId,
                QuestionId = questionId,
                QuestionSource = source,
                Status = status,
                Confidence = confidence,
                IsRevisionNeeded = revisionNeeded,
                IsFavorite = isFavorite,
                LastReviewedAt = DateTime.UtcNow
            };
            db.UserProgresses.Add(existing);
        }

        await db.SaveChangesAsync();
        return existing;
    }

    public async Task<IReadOnlyList<UserProgress>> GetRevisionQueueAsync(string userId)
    {
        return await db.UserProgresses
            .Where(p => p.UserId == userId && p.IsRevisionNeeded)
            .OrderByDescending(p => p.UpdatedAt)
            .ToListAsync();
    }

    public async Task<IReadOnlyList<UserProgress>> GetFavoritesAsync(string userId)
    {
        return await db.UserProgresses
            .Where(p => p.UserId == userId && p.IsFavorite)
            .OrderByDescending(p => p.UpdatedAt)
            .ToListAsync();
    }

    public async Task<Dictionary<string, ProgressStatus>> GetStatusMapAsync(string userId, string categoryId, string source = "category")
    {
        var records = await db.UserProgresses
            .Where(p => p.UserId == userId && p.QuestionSource == source &&
                        p.QuestionId.StartsWith(categoryId + "-"))
            .ToListAsync();

        return records.ToDictionary(p => p.QuestionId, p => p.Status);
    }
}
