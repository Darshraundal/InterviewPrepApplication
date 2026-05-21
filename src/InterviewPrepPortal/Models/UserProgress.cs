namespace InterviewPrepPortal.Models;

public class UserProgress
{
    public int Id { get; set; }
    public string UserId { get; set; } = string.Empty;

    /// <summary>Question ID string e.g. "di-001" or "foliotrack-dotnet-001"</summary>
    public string QuestionId { get; set; } = string.Empty;

    /// <summary>"category" or "project"</summary>
    public string QuestionSource { get; set; } = string.Empty;

    public ProgressStatus Status { get; set; } = ProgressStatus.NotStarted;
    public ConfidenceLevel Confidence { get; set; } = ConfidenceLevel.None;
    public bool IsRevisionNeeded { get; set; }
    public bool IsFavorite { get; set; }
    public DateTime? LastReviewedAt { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ApplicationUser User { get; set; } = null!;
}

public enum ProgressStatus
{
    NotStarted = 0,
    Learning = 1,
    Mastered = 2
}

public enum ConfidenceLevel
{
    None = 0,
    Low = 1,
    Medium = 2,
    High = 3
}
