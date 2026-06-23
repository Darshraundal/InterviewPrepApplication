using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class SearchPage : ContentPage
{
    private readonly SearchViewModel _viewModel;

    public SearchPage(SearchViewModel viewModel)
    {
        InitializeComponent();
        _viewModel = viewModel;
        BindingContext = viewModel;
    }

    private async void OnQuestionTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not QuestionRowViewModel row) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={row.Id}&source={row.Source}");
    }
}
