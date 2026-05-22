using System.Text.Json.Serialization;

namespace InterviewPrepPortal.JsonModels;

public class Question
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("category")]
    public string Category { get; set; } = string.Empty;

    [JsonPropertyName("difficulty")]
    public string Difficulty { get; set; } = string.Empty;

    [JsonPropertyName("frequency")]
    public string Frequency { get; set; } = string.Empty;

    [JsonPropertyName("question")]
    public string QuestionText { get; set; } = string.Empty;

    [JsonPropertyName("answer")]
    public string Answer { get; set; } = string.Empty;

    [JsonPropertyName("projectExample")]
    public ProjectExample? ProjectExample { get; set; }

    [JsonPropertyName("followUps")]
    public List<FollowUp> FollowUps { get; set; } = [];

    [JsonPropertyName("followUpAnswers")]
    public Dictionary<string, string> FollowUpAnswers { get; set; } = [];

    [JsonPropertyName("tip")]
    public string? Tip { get; set; }

    [JsonPropertyName("tags")]
    public List<string> Tags { get; set; } = [];

    [JsonPropertyName("crossReferenceIds")]
    public List<string> CrossReferenceIds { get; set; } = [];

    [JsonPropertyName("sortOrder")]
    public int SortOrder { get; set; }

    [JsonPropertyName("isActive")]
    public bool IsActive { get; set; } = true;
}

public class ProjectExample
{
    [JsonPropertyName("source")]
    public string Source { get; set; } = string.Empty;

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

public class FollowUp
{
    [JsonPropertyName("question")]
    public string Question { get; set; } = string.Empty;

    [JsonPropertyName("answer")]
    public string Answer { get; set; } = string.Empty;
}

public class QuestionsFile
{
    [JsonPropertyName("categoryId")]
    public string CategoryId { get; set; } = string.Empty;

    [JsonPropertyName("questions")]
    public List<Question> Questions { get; set; } = [];
}
