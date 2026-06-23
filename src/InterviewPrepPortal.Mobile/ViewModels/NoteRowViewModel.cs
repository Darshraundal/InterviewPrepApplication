namespace InterviewPrepPortal.Mobile.ViewModels;

public class NoteRowViewModel
{
    public int NoteId { get; init; }
    public string QuestionId { get; init; } = string.Empty;
    public string Source { get; init; } = string.Empty;
    public string QuestionText { get; init; } = string.Empty;
    public string NoteText { get; init; } = string.Empty;
}
