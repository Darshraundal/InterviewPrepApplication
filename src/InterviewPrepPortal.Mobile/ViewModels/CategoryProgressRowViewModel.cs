using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.Mobile.ViewModels;

public class CategoryProgressRowViewModel
{
    public Category Category { get; init; } = null!;
    public int Mastered { get; init; }
    public int Total { get; init; }
    public double Percent => Total > 0 ? Math.Round((double)Mastered / Total * 100, 0) : 0;
    public string CountLabel => $"{Mastered}/{Total}";
}
