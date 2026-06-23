using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Mobile.Services;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class ProjectDetailViewModel(
    IProjectGuideService projectGuideService,
    IProgressService progressService,
    ICustomAnswerService customAnswerService,
    INoteService noteService)
    : ObservableObject, IQueryAttributable
{
    private string _slug = string.Empty;
    private List<ProjectQuestion> _allQuestions = [];

    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private ProjectGuide? _project;

    [ObservableProperty]
    private ProjectDetail? _detail;

    [ObservableProperty]
    private string _searchText = string.Empty;

    [ObservableProperty]
    private string _selectedSection = "All";

    public ObservableCollection<string> Sections { get; } = ["All"];
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
            Project = await projectGuideService.GetProjectBySlugAsync(_slug);
            if (Project == null) return;

            Detail = await projectGuideService.GetProjectDetailAsync(_slug);

            Sections.Clear();
            Sections.Add("All");
            if (Detail != null)
                foreach (var s in Detail.Sections.OrderBy(s => s.SortOrder))
                    Sections.Add(s.Name);

            _allQuestions = (await projectGuideService.GetQuestionsByProjectAsync(Project.Id))
                .OrderBy(q => q.SortOrder)
                .ToList();

            await RefreshQuestionsAsync();
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task RefreshQuestionsAsync()
    {
        var filtered = _allQuestions.AsEnumerable();

        if (SelectedSection != "All")
            filtered = filtered.Where(q => q.Section == SelectedSection);

        if (!string.IsNullOrWhiteSpace(SearchText))
        {
            var s = SearchText;
            filtered = filtered.Where(q => q.QuestionText.Contains(s, StringComparison.OrdinalIgnoreCase));
        }

        Questions.Clear();
        var number = 1;
        foreach (var q in filtered)
        {
            var progress = await progressService.GetProgressAsync(LocalUser.Id, q.Id, "project");
            var customAnswer = await customAnswerService.GetCustomAnswerAsync(LocalUser.Id, q.Id, "project");
            var note = await noteService.GetNoteAsync(LocalUser.Id, q.Id, "project");

            Questions.Add(new QuestionRowViewModel
            {
                Id = q.Id,
                Source = "project",
                Number = number++,
                QuestionText = q.QuestionText,
                Difficulty = q.Difficulty,
                Frequency = q.Frequency,
                Status = progress?.Status ?? ProgressStatus.NotStarted,
                IsFavorite = progress?.IsFavorite ?? false,
                IsRevisionNeeded = progress?.IsRevisionNeeded ?? false,
                HasCustomAnswer = customAnswer != null,
                HasNote = note != null
            });
        }
    }

    [RelayCommand]
    public async Task FilterChangedAsync()
    {
        await RefreshQuestionsAsync();
    }

    partial void OnSelectedSectionChanged(string value) => _ = RefreshQuestionsAsync();

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
