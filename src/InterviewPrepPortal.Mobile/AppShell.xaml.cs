using InterviewPrepPortal.Mobile.Pages;

namespace InterviewPrepPortal.Mobile;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();

        Routing.RegisterRoute(nameof(CategoryDetailPage), typeof(CategoryDetailPage));
        Routing.RegisterRoute(nameof(QuestionDetailPage), typeof(QuestionDetailPage));
        Routing.RegisterRoute(nameof(ProjectDetailPage), typeof(ProjectDetailPage));
        Routing.RegisterRoute(nameof(FavoritesPage), typeof(FavoritesPage));
        Routing.RegisterRoute(nameof(RevisionQueuePage), typeof(RevisionQueuePage));
        Routing.RegisterRoute(nameof(NotesPage), typeof(NotesPage));
    }
}
