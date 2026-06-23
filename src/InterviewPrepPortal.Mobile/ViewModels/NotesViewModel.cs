using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Services;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class NotesViewModel(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    INoteService noteService)
    : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    public ObservableCollection<NoteRowViewModel> Notes { get; } = [];

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            var notes = await noteService.GetAllNotesAsync(LocalUser.Id);

            Notes.Clear();
            foreach (var n in notes)
            {
                var text = await ResolveQuestionTextAsync(n.QuestionId, n.QuestionSource);
                Notes.Add(new NoteRowViewModel
                {
                    NoteId = n.Id,
                    QuestionId = n.QuestionId,
                    Source = n.QuestionSource,
                    QuestionText = text,
                    NoteText = n.NoteText
                });
            }
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    public async Task DeleteNoteAsync(NoteRowViewModel row)
    {
        await noteService.DeleteNoteAsync(row.NoteId, LocalUser.Id);
        Notes.Remove(row);
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
