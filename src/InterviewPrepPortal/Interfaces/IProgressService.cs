using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Interfaces;

public interface IProgressService
{
    Task<UserProgress?> GetProgressAsync(string userId, string questionId, string source);
    Task<IReadOnlyList<UserProgress>> GetAllProgressAsync(string userId);
    Task<ProgressSummary> GetProgressSummaryAsync(string userId);
    Task<CategoryProgressSummary> GetCategoryProgressAsync(string userId, string categoryId);
    Task<UserProgress> UpsertProgressAsync(string userId, string questionId, string source,
        ProgressStatus status, ConfidenceLevel confidence, bool revisionNeeded, bool isFavorite);
    Task<IReadOnlyList<UserProgress>> GetRevisionQueueAsync(string userId);
    Task<IReadOnlyList<UserProgress>> GetFavoritesAsync(string userId);
    Task<Dictionary<string, ProgressStatus>> GetStatusMapAsync(string userId, string categoryId, string source = "category");
}

public record ProgressSummary(
    int TotalCategoryQuestions,
    int TotalProjectQuestions,
    int Mastered,
    int Learning,
    int NotStarted,
    double MasteredPercent,
    int RevisionNeeded,
    int Favorites);

public record CategoryProgressSummary(
    string CategoryId,
    int Total,
    int Mastered,
    int Learning,
    int NotStarted);
