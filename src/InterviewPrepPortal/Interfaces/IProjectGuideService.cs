using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.Interfaces;

public interface IProjectGuideService
{
    Task<IReadOnlyList<ProjectGuide>> GetAllProjectsAsync();
    Task<ProjectGuide?> GetProjectBySlugAsync(string slug);
    Task<ProjectDetail?> GetProjectDetailAsync(string slug);
    Task<IReadOnlyList<ProjectQuestion>> GetQuestionsByProjectAsync(string projectId);
    Task<ProjectQuestion?> GetProjectQuestionByIdAsync(string questionId);
    Task<IReadOnlyList<ProjectQuestion>> SearchProjectQuestionsAsync(string query, string? projectId = null);
}
