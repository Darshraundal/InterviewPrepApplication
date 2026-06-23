using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Mobile.Services;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class CategoryDetailViewModel(
    IQuestionService questionService,
    IProgressService progressService,
    ICustomAnswerService customAnswerService,
    INoteService noteService)
    : ObservableObject, IQueryAttributable
{
    private string _slug = string.Empty;

    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private Category? _category;

    [ObservableProperty]
    private string _searchText = string.Empty;

    public ObservableCollection<QuestionRowViewModel> Questions { get; } = [];

    public void ApplyQueryAttributes(IDictionary<string, object> query)
    {
        if (query.TryGetValue("slug", out var slug))
            _slug = Uri.UnescapeDataString(slug?.ToString() ?? string.Empty);
    }

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy || string.IsNullOrEmpty(_slug)) return;
        IsBusy = true;
        try
        {
            Category = await questionService.GetCategoryBySlugAsync(_slug);
            if (Category == null) return;

            var questions = await questionService.GetQuestionsByCategoryAsync(Category.Id);
            if (!string.IsNullOrWhiteSpace(SearchText))
            {
                var q = SearchText.ToLowerInvariant();
                questions = questions.Where(x => x.QuestionText.Contains(q, StringComparison.OrdinalIgnoreCase)).ToList();
            }

            Questions.Clear();
            var number = 1;
            foreach (var question in questions)
            {
                var progress = await progressService.GetProgressAsync(LocalUser.Id, question.Id, "category");
                var customAnswer = await customAnswerService.GetCustomAnswerAsync(LocalUser.Id, question.Id, "category");
                var note = await noteService.GetNoteAsync(LocalUser.Id, question.Id, "category");

                Questions.Add(new QuestionRowViewModel
                {
                    Id = question.Id,
                    Source = "category",
                    Number = number++,
                    QuestionText = question.QuestionText,
                    Difficulty = question.Difficulty,
                    Frequency = question.Frequency,
                    Status = progress?.Status ?? ProgressStatus.NotStarted,
                    IsFavorite = progress?.IsFavorite ?? false,
                    IsRevisionNeeded = progress?.IsRevisionNeeded ?? false,
                    HasCustomAnswer = customAnswer != null,
                    HasNote = note != null
                });
            }
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    public async Task ToggleFavoriteAsync(QuestionRowViewModel row)
    {
        var existing = await progressService.GetProgressAsync(LocalUser.Id, row.Id, row.Source);
        var newValue = !row.IsFavorite;
        await progressService.UpsertProgressAsync(LocalUser.Id, row.Id, row.Source,
            existing?.Status ?? ProgressStatus.NotStarted,
            existing?.Confidence ?? ConfidenceLevel.None,
            existing?.IsRevisionNeeded ?? false,
            newValue);
        row.IsFavorite = newValue;
    }
}
