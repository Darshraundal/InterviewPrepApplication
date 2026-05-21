using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.ViewModels.Search;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class SearchController(ISearchService searchService) : Controller
{
    public async Task<IActionResult> Results(string? q, string? scope)
    {
        if (string.IsNullOrWhiteSpace(q))
            return View(new SearchResultViewModel
            {
                Result = new SearchResult(string.Empty, [], [], 0),
                ScopeFilter = scope
            });

        var searchScope = scope switch
        {
            "category" => SearchScope.CategoryQuestions,
            "project" => SearchScope.ProjectQuestions,
            _ => SearchScope.All
        };

        var result = await searchService.SearchAsync(q, searchScope);
        return View(new SearchResultViewModel { Result = result, ScopeFilter = scope });
    }
}
