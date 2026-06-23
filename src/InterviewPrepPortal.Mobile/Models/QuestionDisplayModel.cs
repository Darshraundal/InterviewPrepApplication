using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.Mobile.Models;

/// <summary>
/// Category questions (Question) and project questions (ProjectQuestion) are two
/// distinct JSON shapes with slightly different field names (see JsonModels). The
/// detail page and list rows need to render both the same way, so this DTO
/// normalizes either source into one shape.
/// </summary>
public class QuestionDisplayModel
{
    public string Id { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty; // "category" | "project"
    public string ParentId { get; set; } = string.Empty; // categoryId or projectId
    public string GroupLabel { get; set; } = string.Empty; // category name or section name
    public string QuestionText { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
    public string Difficulty { get; set; } = string.Empty;
    public string Frequency { get; set; } = string.Empty;
    public List<string> Tags { get; set; } = [];
    public string? Tip { get; set; }
    public int SortOrder { get; set; }

    public string? ExampleSource { get; set; }
    public string? ExampleFile { get; set; }
    public string? ExampleClassName { get; set; }
    public string? ExampleMethod { get; set; }
    public string? ExampleCode { get; set; }
    public string? ExampleExplanation { get; set; }
    public bool HasExample => !string.IsNullOrWhiteSpace(ExampleCode) || !string.IsNullOrWhiteSpace(ExampleExplanation);

    public List<FollowUpItem> FollowUps { get; set; } = [];
    public List<string> CrossReferenceIds { get; set; } = [];

    public static QuestionDisplayModel FromCategoryQuestion(Question q, string categoryName)
    {
        return new QuestionDisplayModel
        {
            Id = q.Id,
            Source = "category",
            ParentId = q.Category,
            GroupLabel = categoryName,
            QuestionText = q.QuestionText,
            Answer = q.Answer,
            Difficulty = q.Difficulty,
            Frequency = q.Frequency,
            Tags = q.Tags,
            Tip = q.Tip,
            SortOrder = q.SortOrder,
            ExampleSource = q.ProjectExample?.Source,
            ExampleFile = q.ProjectExample?.File,
            ExampleClassName = q.ProjectExample?.ClassName,
            ExampleMethod = q.ProjectExample?.Method,
            ExampleCode = q.ProjectExample?.Code,
            ExampleExplanation = q.ProjectExample?.Explanation,
            FollowUps = q.FollowUps.Select(f => new FollowUpItem(f.Question, f.Answer)).ToList(),
            CrossReferenceIds = q.CrossReferenceIds
        };
    }

    public static QuestionDisplayModel FromProjectQuestion(ProjectQuestion q, string sectionName)
    {
        return new QuestionDisplayModel
        {
            Id = q.Id,
            Source = "project",
            ParentId = q.ProjectId,
            GroupLabel = sectionName,
            QuestionText = q.QuestionText,
            Answer = q.Answer,
            Difficulty = q.Difficulty,
            Frequency = q.Frequency,
            Tags = q.Tags,
            Tip = q.ImportantForInterview,
            SortOrder = q.SortOrder,
            ExampleFile = q.ProjectExample?.File,
            ExampleClassName = q.ProjectExample?.ClassName,
            ExampleMethod = q.ProjectExample?.Method,
            ExampleCode = q.ProjectExample?.Code,
            ExampleExplanation = q.ProjectExample?.Explanation,
            FollowUps = q.FollowUps.Select(f => new FollowUpItem(f, string.Empty)).ToList(),
            CrossReferenceIds = []
        };
    }
}

public record FollowUpItem(string Question, string Answer);
