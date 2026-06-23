using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.Interfaces;

public interface ISearchService
{
    Task<SearchResult> SearchAsync(string query, SearchScope scope = SearchScope.All);
}

public enum SearchScope { All, CategoryQuestions, ProjectQuestions }

public record SearchResult(
    string Query,
    IReadOnlyList<Question> CategoryMatches,
    IReadOnlyList<ProjectQuestion> ProjectMatches,
    int TotalCount);
