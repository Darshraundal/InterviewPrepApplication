using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.ViewModels.Project;

public class ProjectDetailViewModel
{
    public ProjectGuide Project { get; set; } = null!;
    public ProjectDetail Detail { get; set; } = null!;
    public List<ProjectSectionWithQuestions> Sections { get; set; } = [];
    public int TotalQuestions { get; set; }
    public int MasteredCount { get; set; }
    public string? ActiveSection { get; set; }
    public string? SearchQuery { get; set; }
}

public class ProjectSectionWithQuestions
{
    public ProjectSection Section { get; set; } = null!;
    public List<ProjectQuestionWithUserData> Questions { get; set; } = [];
}

public class ProjectQuestionWithUserData
{
    public ProjectQuestion Question { get; set; } = null!;
    public UserProgress? Progress { get; set; }
    public bool HasCustomAnswer { get; set; }
    public bool HasNote { get; set; }
}
