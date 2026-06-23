using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class CategoryDetailPage : ContentPage
{
    private readonly CategoryDetailViewModel _viewModel;

    public CategoryDetailPage(CategoryDetailViewModel viewModel)
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

    private async void OnFavoriteTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not QuestionRowViewModel row) return;
        await _viewModel.ToggleFavoriteCommand.ExecuteAsync(row);
    }
}
