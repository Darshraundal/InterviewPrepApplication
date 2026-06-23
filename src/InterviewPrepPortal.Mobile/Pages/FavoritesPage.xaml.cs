using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class FavoritesPage : ContentPage
{
    private readonly FavoritesViewModel _viewModel;

    public FavoritesPage(FavoritesViewModel viewModel)
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

    private async void OnQuestionTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not QuestionRowViewModel row) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={row.Id}&source={row.Source}");
    }
}
