using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.ViewModels.Category;

namespace InterviewPrepPortal.ViewModels.Progress;

public class ProgressDashboardViewModel
{
    public ProgressSummary Overall { get; set; } = null!;
    public List<CategoryProgressItem> PerCategory { get; set; } = [];
    public List<QuestionWithUserData> RevisionQueue { get; set; } = [];
    public List<QuestionWithUserData> Favorites { get; set; } = [];
    public List<UserNote> RecentNotes { get; set; } = [];
}

public class CategoryProgressItem
{
    public string CategoryId { get; set; } = string.Empty;
    public string CategoryName { get; set; } = string.Empty;
    public string Emoji { get; set; } = string.Empty;
    public CategoryProgressSummary Summary { get; set; } = null!;
    public int TotalQuestions { get; set; }  // total from JSON, not just tracked
}
