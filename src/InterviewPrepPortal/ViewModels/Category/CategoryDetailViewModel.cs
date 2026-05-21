using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using Q = InterviewPrepPortal.JsonModels.Question;
using Cat = InterviewPrepPortal.JsonModels.Category;

namespace InterviewPrepPortal.ViewModels.Category;

public class CategoryDetailViewModel
{
    public Cat Category { get; set; } = null!;
    public List<QuestionWithUserData> Questions { get; set; } = [];
    public CategoryProgressSummary Progress { get; set; } = null!;
    public string? SearchQuery { get; set; }
    public string? DifficultyFilter { get; set; }
    public string? FrequencyFilter { get; set; }
    public string? StatusFilter { get; set; }
    public int TotalCount { get; set; }
    public int FilteredCount { get; set; }
}

public class QuestionWithUserData
{
    public Q Question { get; set; } = null!;
    public UserProgress? Progress { get; set; }
    public bool HasCustomAnswer { get; set; }
    public bool HasNote { get; set; }
}
