using InterviewPrepPortal.Interfaces;

namespace InterviewPrepPortal.Services;

public class SearchService(IQuestionService questionService, IProjectGuideService projectGuideService) : ISearchService
{
    public async Task<SearchResult> SearchAsync(string query, SearchScope scope = SearchScope.All)
    {
        if (string.IsNullOrWhiteSpace(query))
            return new SearchResult(query, [], [], 0);

        var categoryTask = scope != SearchScope.ProjectQuestions
            ? questionService.SearchQuestionsAsync(query)
            : Task.FromResult<IReadOnlyList<JsonModels.Question>>([]);

        var projectTask = scope != SearchScope.CategoryQuestions
            ? projectGuideService.SearchProjectQuestionsAsync(query)
            : Task.FromResult<IReadOnlyList<JsonModels.ProjectQuestion>>([]);

        await Task.WhenAll(categoryTask, projectTask);

        var catMatches = await categoryTask;
        var projMatches = await projectTask;

        return new SearchResult(query, catMatches, projMatches, catMatches.Count + projMatches.Count);
    }
}
