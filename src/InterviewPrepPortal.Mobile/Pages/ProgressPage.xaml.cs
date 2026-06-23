using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class ProgressPage : ContentPage
{
    private readonly ProgressViewModel _viewModel;

    public ProgressPage(ProgressViewModel viewModel)
    {
        InitializeComponent();
        _viewModel = viewModel;
        BindingContext = viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await _viewModel.LoadCommand.ExecuteAsync(null);
    }

    private async void OnCategoryTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not CategoryProgressRowViewModel row) return;
        await Shell.Current.GoToAsync($"{nameof(CategoryDetailPage)}?slug={row.Category.Slug}");
    }

    private async void OnRevisionTapped(object? sender, TappedEventArgs e) =>
        await Shell.Current.GoToAsync(nameof(RevisionQueuePage));

    private async void OnFavoritesTapped(object? sender, TappedEventArgs e) =>
        await Shell.Current.GoToAsync(nameof(FavoritesPage));

    private async void OnNotesTapped(object? sender, TappedEventArgs e) =>
        await Shell.Current.GoToAsync(nameof(NotesPage));
}
