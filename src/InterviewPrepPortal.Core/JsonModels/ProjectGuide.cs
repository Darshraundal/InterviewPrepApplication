using System.Text.Json.Serialization;

namespace InterviewPrepPortal.JsonModels;

public class ProjectGuide
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("slug")]
    public string Slug { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("subtitle")]
    public string Subtitle { get; set; } = string.Empty;

    [JsonPropertyName("stack")]
    public List<string> Stack { get; set; } = [];

    [JsonPropertyName("stackSummary")]
    public string StackSummary { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    [JsonPropertyName("dataFile")]
    public string DataFile { get; set; } = string.Empty;

    [JsonPropertyName("questionCount")]
    public int QuestionCount { get; set; }

    [JsonPropertyName("difficulty")]
    public string Difficulty { get; set; } = string.Empty;

    [JsonPropertyName("tags")]
    public List<string> Tags { get; set; } = [];

    [JsonPropertyName("sortOrder")]
    public int SortOrder { get; set; }

    [JsonPropertyName("isActive")]
    public bool IsActive { get; set; } = true;
}

public class ProjectsIndex
{
    [JsonPropertyName("projects")]
    public List<ProjectGuide> Projects { get; set; } = [];
}

public class ProjectDetail
{
    [JsonPropertyName("projectId")]
    public string ProjectId { get; set; } = string.Empty;

    [JsonPropertyName("architectureSummary")]
    public ArchitectureSummary? ArchitectureSummary { get; set; }

    [JsonPropertyName("sections")]
    public List<ProjectSection> Sections { get; set; } = [];

    [JsonPropertyName("questions")]
    public List<ProjectQuestion> Questions { get; set; } = [];
}

public class ArchitectureSummary
{
    [JsonPropertyName("overview")]
    public string Overview { get; set; } = string.Empty;

    [JsonPropertyName("requestLifecycle")]
    public string? RequestLifecycle { get; set; }

    [JsonPropertyName("authFlow")]
    public string? AuthFlow { get; set; }

    [JsonPropertyName("databaseFlow")]
    public string? DatabaseFlow { get; set; }

    [JsonPropertyName("diagramText")]
    public string? DiagramText { get; set; }
}

public class ProjectSection
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("sortOrder")]
    public int SortOrder { get; set; }
}
