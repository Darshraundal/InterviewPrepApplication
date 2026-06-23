using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Mobile.Services;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class HomeViewModel(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    IProgressService progressService)
    : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private ProgressSummary _overall = new(0, 0, 0, 0, 0, 0, 0, 0);

    public ObservableCollection<CategoryProgressRowViewModel> Categories { get; } = [];
    public ObservableCollection<QuestionRowViewModel> RevisionQueue { get; } = [];
    public ObservableCollection<QuestionRowViewModel> RecentFavorites { get; } = [];
    public ObservableCollection<ProjectGuide> Projects { get; } = [];

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            var categories = (await questionService.GetCategoriesAsync())
                .OrderBy(c => c.SortOrder)
                .Take(10)
                .ToList();

            Categories.Clear();
            foreach (var cat in categories)
            {
                var summary = await progressService.GetCategoryProgressAsync(LocalUser.Id, cat.Id);
                var total = (await questionService.GetQuestionsByCategoryAsync(cat.Id)).Count;
                Categories.Add(new CategoryProgressRowViewModel { Category = cat, Mastered = summary.Mastered, Total = total });
            }

            Overall = await progressService.GetProgressSummaryAsync(LocalUser.Id);

            var revision = await progressService.GetRevisionQueueAsync(LocalUser.Id);
            RevisionQueue.Clear();
            foreach (var p in revision.Take(8))
            {
                var text = await ResolveQuestionTextAsync(p.QuestionId, p.QuestionSource);
                RevisionQueue.Add(new QuestionRowViewModel
                {
                    Id = p.QuestionId,
                    Source = p.QuestionSource,
                    QuestionText = Truncate(text, 70),
                    Status = p.Status,
                    IsFavorite = p.IsFavorite,
                    IsRevisionNeeded = p.IsRevisionNeeded
                });
            }

            var favorites = await progressService.GetFavoritesAsync(LocalUser.Id);
            RecentFavorites.Clear();
            foreach (var p in favorites.Take(5))
            {
                var text = await ResolveQuestionTextAsync(p.QuestionId, p.QuestionSource);
                RecentFavorites.Add(new QuestionRowViewModel
                {
                    Id = p.QuestionId,
                    Source = p.QuestionSource,
                    QuestionText = Truncate(text, 70),
                    Status = p.Status,
                    IsFavorite = p.IsFavorite,
                    IsRevisionNeeded = p.IsRevisionNeeded
                });
            }

            Projects.Clear();
            foreach (var proj in await projectGuideService.GetAllProjectsAsync())
                Projects.Add(proj);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task<string> ResolveQuestionTextAsync(string questionId, string source)
    {
        if (source == "category")
        {
            var q = await questionService.GetQuestionByIdAsync(questionId);
            return q?.QuestionText ?? questionId;
        }

        var pq = await projectGuideService.GetProjectQuestionByIdAsync(questionId);
        return pq?.QuestionText ?? questionId;
    }

    private static string Truncate(string text, int max) =>
        text.Length <= max ? text : text[..max] + "…";
}
