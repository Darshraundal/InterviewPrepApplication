using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class NotesPage : ContentPage
{
    private readonly NotesViewModel _viewModel;

    public NotesPage(NotesViewModel viewModel)
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
        if ((sender as Element)?.BindingContext is not NoteRowViewModel row) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={row.QuestionId}&source={row.Source}");
    }

    private async void OnDeleteTapped(object? sender, EventArgs e)
    {
        if ((sender as Element)?.BindingContext is not NoteRowViewModel row) return;
        var confirmed = await DisplayAlert("Delete note", "Remove this note?", "Delete", "Cancel");
        if (!confirmed) return;
        await _viewModel.DeleteNoteCommand.ExecuteAsync(row);
    }
}
