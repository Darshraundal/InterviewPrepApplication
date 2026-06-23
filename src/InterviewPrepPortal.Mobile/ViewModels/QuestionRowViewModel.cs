using CommunityToolkit.Mvvm.ComponentModel;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Mobile.ViewModels;

/// <summary>
/// Lightweight row used in every question list (category detail, project detail,
/// search results, favorites, revision queue, home widgets).
/// </summary>
public partial class QuestionRowViewModel : ObservableObject
{
    public string Id { get; init; } = string.Empty;
    public string Source { get; init; } = string.Empty; // "category" | "project"
    public int Number { get; init; }
    public string QuestionText { get; init; } = string.Empty;
    public string Difficulty { get; init; } = string.Empty;
    public string Frequency { get; init; } = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(StatusGlyph))]
    private ProgressStatus _status;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(FavoriteGlyph))]
    private bool _isFavorite;

    [ObservableProperty]
    private bool _isRevisionNeeded;

    public bool HasNote { get; init; }
    public bool HasCustomAnswer { get; init; }

    public string StatusGlyph => Status switch
    {
        ProgressStatus.Mastered => "✓ Mastered",
        ProgressStatus.Learning => "⚡ Learning",
        _ => "Not started"
    };

    public string FavoriteGlyph => IsFavorite ? "★" : "☆";
}
