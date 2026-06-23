using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class QuestionDetailPage : ContentPage
{
    private readonly QuestionDetailViewModel _viewModel;

    public QuestionDetailPage(QuestionDetailViewModel viewModel)
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

    private async void OnConfidenceChanged(object? sender, EventArgs e)
    {
        await _viewModel.ConfidenceChangedCommand.ExecuteAsync(null);
    }

    private async void OnCrossReferenceTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not CrossReferenceItem item) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={item.Id}&source=category");
    }

    private async void OnPreviousTapped(object? sender, EventArgs e)
    {
        if (_viewModel.PreviousQuestion is not { } row) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={row.Id}&source={row.Source}");
    }

    private async void OnNextTapped(object? sender, EventArgs e)
    {
        if (_viewModel.NextQuestion is not { } row) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={row.Id}&source={row.Source}");
    }
}
