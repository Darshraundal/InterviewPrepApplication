using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.Interfaces;

public interface IQuestionService
{
    Task<IReadOnlyList<Category>> GetCategoriesAsync();
    Task<Category?> GetCategoryBySlugAsync(string slug);
    Task<Category?> GetCategoryByIdAsync(string id);
    Task<IReadOnlyList<Question>> GetQuestionsByCategoryAsync(string categoryId);
    Task<Question?> GetQuestionByIdAsync(string questionId);
    Task<IReadOnlyList<Question>> GetAllQuestionsAsync();
    Task<IReadOnlyList<Question>> GetQuestionsByIdsAsync(IEnumerable<string> ids);
    Task<IReadOnlyList<Question>> SearchQuestionsAsync(string query, string? categoryId = null,
        string? difficulty = null, string? frequency = null);
}
