using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Services;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class FavoritesViewModel(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    IProgressService progressService)
    : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    public ObservableCollection<QuestionRowViewModel> Favorites { get; } = [];

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            var favorites = await progressService.GetFavoritesAsync(LocalUser.Id);

            Favorites.Clear();
            foreach (var p in favorites)
            {
                var text = await ResolveQuestionTextAsync(p.QuestionId, p.QuestionSource);
                Favorites.Add(new QuestionRowViewModel
                {
                    Id = p.QuestionId,
                    Source = p.QuestionSource,
                    QuestionText = text,
                    Status = p.Status,
                    IsFavorite = p.IsFavorite,
                    IsRevisionNeeded = p.IsRevisionNeeded
                });
            }
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
}
