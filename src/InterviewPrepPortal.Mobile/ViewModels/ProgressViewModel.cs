using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Services;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class ProgressViewModel(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    IProgressService progressService,
    INoteService noteService)
    : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private ProgressSummary _overall = new(0, 0, 0, 0, 0, 0, 0, 0);

    public ObservableCollection<CategoryProgressRowViewModel> Categories { get; } = [];
    public ObservableCollection<QuestionRowViewModel> RevisionQueue { get; } = [];
    public ObservableCollection<QuestionRowViewModel> Favorites { get; } = [];
    public int NoteCount { get; private set; }

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            Overall = await progressService.GetProgressSummaryAsync(LocalUser.Id);

            var categories = (await questionService.GetCategoriesAsync()).OrderBy(c => c.SortOrder).ToList();
            Categories.Clear();
            foreach (var cat in categories)
            {
                var summary = await progressService.GetCategoryProgressAsync(LocalUser.Id, cat.Id);
                var total = (await questionService.GetQuestionsByCategoryAsync(cat.Id)).Count;
                Categories.Add(new CategoryProgressRowViewModel { Category = cat, Mastered = summary.Mastered, Total = total });
            }

            var revision = await progressService.GetRevisionQueueAsync(LocalUser.Id);
            RevisionQueue.Clear();
            foreach (var p in revision.Take(5))
            {
                var text = await ResolveQuestionTextAsync(p.QuestionId, p.QuestionSource);
                RevisionQueue.Add(new QuestionRowViewModel
                {
                    Id = p.QuestionId,
                    Source = p.QuestionSource,
                    QuestionText = text,
                    Status = p.Status,
                    IsFavorite = p.IsFavorite,
                    IsRevisionNeeded = p.IsRevisionNeeded
                });
            }

            var favorites = await progressService.GetFavoritesAsync(LocalUser.Id);
            Favorites.Clear();
            foreach (var p in favorites.Take(5))
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

            NoteCount = (await noteService.GetAllNotesAsync(LocalUser.Id)).Count;
            OnPropertyChanged(nameof(NoteCount));
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
