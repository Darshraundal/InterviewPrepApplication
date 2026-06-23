using System.Text.Json.Serialization;

namespace InterviewPrepPortal.JsonModels;

public class ProjectQuestion
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("projectId")]
    public string ProjectId { get; set; } = string.Empty;

    [JsonPropertyName("section")]
    public string Section { get; set; } = string.Empty;

    [JsonPropertyName("question")]
    public string QuestionText { get; set; } = string.Empty;

    [JsonPropertyName("answer")]
    public string Answer { get; set; } = string.Empty;

    [JsonPropertyName("projectExample")]
    public ProjectQuestionExample? ProjectExample { get; set; }

    [JsonPropertyName("followUps")]
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

public class ProjectQuestionExample
{
    [JsonPropertyName("file")]
    public string? File { get; set; }

    [JsonPropertyName("className")]
    public string? ClassName { get; set; }

    [JsonPropertyName("method")]
    public string? Method { get; set; }

    [JsonPropertyName("code")]
    public string? Code { get; set; }

    [JsonPropertyName("explanation")]
    public string? Explanation { get; set; }
}
