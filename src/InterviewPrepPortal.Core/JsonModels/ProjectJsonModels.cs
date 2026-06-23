using System.Text.Json.Serialization;

namespace InterviewPrepPortal.JsonModels;

/// <summary>
/// JSON-only deserialization model for project data files.
/// The actual JSON structure has questions nested inside sections;
/// these types capture that shape and are mapped to the domain models
/// (ProjectDetail, ProjectSection, ProjectQuestion) in ProjectGuideService.
/// </summary>
internal class ProjectDetailJson
{
    [JsonPropertyName("projectId")]
    public string ProjectId { get; set; } = string.Empty;

    [JsonPropertyName("architectureSummary")]
    public ArchitectureSummary? ArchitectureSummary { get; set; }

    [JsonPropertyName("sections")]
    public List<ProjectSectionJson> Sections { get; set; } = [];
}

internal class ProjectSectionJson
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("questions")]
    public List<ProjectQuestionJson> Questions { get; set; } = [];
}

internal class ProjectQuestionJson
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("projectId")]
    public string ProjectId { get; set; } = string.Empty;

    // JSON uses "questionText", not "question"
    [JsonPropertyName("questionText")]
    public string QuestionText { get; set; } = string.Empty;

    [JsonPropertyName("answer")]
    public string Answer { get; set; } = string.Empty;

    [JsonPropertyName("projectExample")]
    public ProjectQuestionExample? ProjectExample { get; set; }

    // JSON uses "followUpQuestions", not "followUps"
    [JsonPropertyName("followUpQuestions")]
    public List<string> FollowUps { get; set; } = [];

    [JsonPropertyName("importantForInterview")]
    public string? ImportantForInterview { get; set; }

    [JsonPropertyName("difficulty")]
    public string Difficulty { get; set; } = string.Empty;

    [JsonPropertyName("frequency")]
    public string Frequency { get; set; } = string.Empty;

    [JsonPropertyName("tags")]
    public List<string> Tags { get; set; } = [];

    [JsonPropertyName("sortOrder")]
    public int SortOrder { get; set; }

    [JsonPropertyName("isActive")]
    public bool IsActive { get; set; } = true;
}
