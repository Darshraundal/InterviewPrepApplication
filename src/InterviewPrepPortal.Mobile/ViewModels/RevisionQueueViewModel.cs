using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Services;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class RevisionQueueViewModel(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    IProgressService progressService)
    : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    public ObservableCollection<QuestionRowViewModel> RevisionQueue { get; } = [];

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            var revision = await progressService.GetRevisionQueueAsync(LocalUser.Id);

            RevisionQueue.Clear();
            foreach (var p in revision)
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
