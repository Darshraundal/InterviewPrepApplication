using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Models;
using Cat = InterviewPrepPortal.JsonModels.Category;

namespace InterviewPrepPortal.ViewModels.Home;

public class DashboardViewModel
{
    public string UserDisplayName { get; set; } = string.Empty;
    public ProgressSummary OverallProgress { get; set; } = null!;
    public List<CategoryWithProgress> Categories { get; set; } = [];
    public List<ProjectGuide> Projects { get; set; } = [];
    public List<QuestionWithProgress> RevisionQueue { get; set; } = [];
    public List<QuestionWithProgress> RecentFavorites { get; set; } = [];
    public int TotalCategoryQuestions { get; set; }
    public int TotalProjectQuestions { get; set; }
}

public class CategoryWithProgress
{
    public Cat Category { get; set; } = null!;
    public CategoryProgressSummary Progress { get; set; } = null!;
    public int TotalQuestions { get; set; }
}

public class QuestionWithProgress
{
    public string QuestionId { get; set; } = string.Empty;
    public string QuestionText { get; set; } = string.Empty;
    public string CategoryId { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;   // "category" | "project"
    public UserProgress? Progress { get; set; }
}
