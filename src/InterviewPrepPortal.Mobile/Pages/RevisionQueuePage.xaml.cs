using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class RevisionQueuePage : ContentPage
{
    private readonly RevisionQueueViewModel _viewModel;

    public RevisionQueuePage(RevisionQueueViewModel viewModel)
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
