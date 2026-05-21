using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.ViewModels.Search;

public class SearchResultViewModel
{
    public SearchResult Result { get; set; } = null!;
    public string? ScopeFilter { get; set; }
}
