using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Models;
using InterviewPrepPortal.Mobile.Services;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class QuestionDetailViewModel(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    IProgressService progressService,
    ICustomAnswerService customAnswerService,
    INoteService noteService)
    : ObservableObject, IQueryAttributable
{
    public static readonly string[] ConfidenceOptions = ["None", "Low", "Medium", "High"];

    private string _questionId = string.Empty;
    private string _source = "category";

    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private QuestionDisplayModel? _question;

    [ObservableProperty]
    private ProgressStatus _status;

    [ObservableProperty]
    private int _confidenceIndex;

    [ObservableProperty]
    private bool _isRevisionNeeded;

    [ObservableProperty]
    private bool _isFavorite;

    [ObservableProperty]
    private string _customAnswerText = string.Empty;

    [ObservableProperty]
    private string _noteText = string.Empty;

    [ObservableProperty]
    private string _saveFeedback = string.Empty;

    [ObservableProperty]
    private QuestionRowViewModel? _previousQuestion;

    [ObservableProperty]
    private QuestionRowViewModel? _nextQuestion;

    public ObservableCollection<CrossReferenceItem> CrossReferences { get; } = [];

    public bool IsMastered => Status == ProgressStatus.Mastered;
    public bool IsLearning => Status == ProgressStatus.Learning;

    public void ApplyQueryAttributes(IDictionary<string, object> query)
    {
        if (query.TryGetValue("id", out var id))
            _questionId = Uri.UnescapeDataString(id?.ToString() ?? string.Empty);
        if (query.TryGetValue("source", out var source))
            _source = Uri.UnescapeDataString(source?.ToString() ?? "category");
    }

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy || string.IsNullOrEmpty(_questionId)) return;
        IsBusy = true;
        try
        {
            if (_source == "category")
                await LoadCategoryQuestionAsync();
            else
                await LoadProjectQuestionAsync();

            var progress = await progressService.GetProgressAsync(LocalUser.Id, _questionId, _source);
            Status = progress?.Status ?? ProgressStatus.NotStarted;
            ConfidenceIndex = (int)(progress?.Confidence ?? ConfidenceLevel.None);
            IsRevisionNeeded = progress?.IsRevisionNeeded ?? false;
            IsFavorite = progress?.IsFavorite ?? false;

            var customAnswer = await customAnswerService.GetCustomAnswerAsync(LocalUser.Id, _questionId, _source);
            CustomAnswerText = customAnswer?.AnswerText ?? string.Empty;

            var note = await noteService.GetNoteAsync(LocalUser.Id, _questionId, _source);
            NoteText = note?.NoteText ?? string.Empty;
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadCategoryQuestionAsync()
    {
        var q = await questionService.GetQuestionByIdAsync(_questionId);
        if (q == null) return;

        var category = await questionService.GetCategoryByIdAsync(q.Category);
        Question = QuestionDisplayModel.FromCategoryQuestion(q, category?.Name ?? q.Category);

        CrossReferences.Clear();
        if (q.CrossReferenceIds.Count > 0)
        {
            var refs = await questionService.GetQuestionsByIdsAsync(q.CrossReferenceIds);
            foreach (var r in refs)
                CrossReferences.Add(new CrossReferenceItem(r.Id, r.QuestionText));
        }

        var siblings = (await questionService.GetQuestionsByCategoryAsync(q.Category)).ToList();
        SetPrevNext(siblings.Select(s => (s.Id, s.QuestionText)).ToList(), q.Id, "category");
    }

    private async Task LoadProjectQuestionAsync()
    {
        var q = await projectGuideService.GetProjectQuestionByIdAsync(_questionId);
        if (q == null) return;

        Question = QuestionDisplayModel.FromProjectQuestion(q, q.Section);

        var siblings = (await projectGuideService.GetQuestionsByProjectAsync(q.ProjectId)).ToList();
        SetPrevNext(siblings.Select(s => (s.Id, s.QuestionText)).ToList(), q.Id, "project");
    }

    private void SetPrevNext(List<(string Id, string Text)> ordered, string currentId, string source)
    {
        var index = ordered.FindIndex(x => x.Id == currentId);
        PreviousQuestion = index > 0
            ? new QuestionRowViewModel { Id = ordered[index - 1].Id, Source = source, QuestionText = ordered[index - 1].Text }
            : null;
        NextQuestion = index >= 0 && index < ordered.Count - 1
            ? new QuestionRowViewModel { Id = ordered[index + 1].Id, Source = source, QuestionText = ordered[index + 1].Text }
            : null;
    }

    [RelayCommand]
    public async Task SetStatusAsync(string statusName)
    {
        var newStatus = Status == ParseStatus(statusName) ? ProgressStatus.NotStarted : ParseStatus(statusName);
        Status = newStatus;
        await PersistProgressAsync();
    }

    [RelayCommand]
    public async Task ToggleRevisionAsync()
    {
        IsRevisionNeeded = !IsRevisionNeeded;
        await PersistProgressAsync();
    }

    [RelayCommand]
    public async Task ToggleFavoriteAsync()
    {
        IsFavorite = !IsFavorite;
        await PersistProgressAsync();
    }

    [RelayCommand]
    public async Task ConfidenceChangedAsync()
    {
        await PersistProgressAsync();
    }

    private async Task PersistProgressAsync()
    {
        await progressService.UpsertProgressAsync(LocalUser.Id, _questionId, _source,
            Status, (ConfidenceLevel)ConfidenceIndex, IsRevisionNeeded, IsFavorite);
    }

    private static ProgressStatus ParseStatus(string name) => name switch
    {
        "Learning" => ProgressStatus.Learning,
        "Mastered" => ProgressStatus.Mastered,
        _ => ProgressStatus.NotStarted
    };

    [RelayCommand]
    public async Task SaveCustomAnswerAsync()
    {
        await customAnswerService.SaveCustomAnswerAsync(LocalUser.Id, _questionId, _source, CustomAnswerText);
        await ShowSaveFeedbackAsync();
    }

    [RelayCommand]
    public async Task SaveNoteAsync()
    {
        await noteService.SaveNoteAsync(LocalUser.Id, _questionId, _source, NoteText);
        await ShowSaveFeedbackAsync();
    }

    private async Task ShowSaveFeedbackAsync()
    {
        SaveFeedback = "✓ Saved";
        await Task.Delay(2500);
        SaveFeedback = string.Empty;
    }

    partial void OnStatusChanged(ProgressStatus value)
    {
        OnPropertyChanged(nameof(IsMastered));
        OnPropertyChanged(nameof(IsLearning));
    }
}

public record CrossReferenceItem(string Id, string Text);
