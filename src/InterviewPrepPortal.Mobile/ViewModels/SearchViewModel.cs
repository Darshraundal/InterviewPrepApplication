using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Services;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class SearchViewModel(
    ISearchService searchService,
    IProgressService progressService)
    : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private string _searchText = string.Empty;

    [ObservableProperty]
    private SearchScope _scope = SearchScope.All;

    public ObservableCollection<QuestionRowViewModel> Results { get; } = [];

    [RelayCommand]
    public async Task SearchAsync()
    {
        if (IsBusy || string.IsNullOrWhiteSpace(SearchText))
        {
            Results.Clear();
            return;
        }

        IsBusy = true;
        try
        {
            var result = await searchService.SearchAsync(SearchText, Scope);

            Results.Clear();

            foreach (var q in result.CategoryMatches)
            {
                var progress = await progressService.GetProgressAsync(LocalUser.Id, q.Id, "category");
                Results.Add(new QuestionRowViewModel
                {
                    Id = q.Id,
                    Source = "category",
                    QuestionText = q.QuestionText,
                    Difficulty = q.Difficulty,
                    Frequency = q.Frequency,
                    Status = progress?.Status ?? ProgressStatus.NotStarted,
                    IsFavorite = progress?.IsFavorite ?? false,
                    IsRevisionNeeded = progress?.IsRevisionNeeded ?? false
                });
            }

            foreach (var q in result.ProjectMatches)
            {
                var progress = await progressService.GetProgressAsync(LocalUser.Id, q.Id, "project");
                Results.Add(new QuestionRowViewModel
                {
                    Id = q.Id,
                    Source = "project",
                    QuestionText = q.QuestionText,
                    Difficulty = q.Difficulty,
                    Frequency = q.Frequency,
                    Status = progress?.Status ?? ProgressStatus.NotStarted,
                    IsFavorite = progress?.IsFavorite ?? false,
                    IsRevisionNeeded = progress?.IsRevisionNeeded ?? false
                });
            }
        }
        finally
        {
            IsBusy = false;
        }
    }

    partial void OnScopeChanged(SearchScope value) => _ = SearchAsync();

    [RelayCommand]
    public void SetScope(string scopeName)
    {
        Scope = scopeName switch
        {
            "Category" => SearchScope.CategoryQuestions,
            "Project" => SearchScope.ProjectQuestions,
            _ => SearchScope.All
        };
    }
}
