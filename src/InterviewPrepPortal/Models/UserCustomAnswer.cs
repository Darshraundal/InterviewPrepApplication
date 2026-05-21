namespace InterviewPrepPortal.Models;

public class UserCustomAnswer
{
    public int Id { get; set; }
    public string UserId { get; set; } = string.Empty;
    public string QuestionId { get; set; } = string.Empty;
    public string QuestionSource { get; set; } = string.Empty;

    /// <summary>User's own interview answer in their own words</summary>
    public string AnswerText { get; set; } = string.Empty;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ApplicationUser User { get; set; } = null!;
}
