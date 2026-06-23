using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class ProjectsPage : ContentPage
{
    private readonly ProjectsViewModel _viewModel;

    public ProjectsPage(ProjectsViewModel viewModel)
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

    private async void OnProjectTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not ProjectGuide project) return;
        await Shell.Current.GoToAsync($"{nameof(ProjectDetailPage)}?slug={project.Slug}");
    }
}
