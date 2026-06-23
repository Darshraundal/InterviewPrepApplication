using InterviewPrepPortal.JsonModels;
using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class HomePage : ContentPage
{
    private readonly HomeViewModel _viewModel;

    public HomePage(HomeViewModel viewModel)
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

    private async void OnQuestionTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not QuestionRowViewModel row) return;
        await Shell.Current.GoToAsync($"{nameof(QuestionDetailPage)}?id={row.Id}&source={row.Source}");
    }

    private async void OnProjectTapped(object? sender, TappedEventArgs e)
    {
        if ((sender as Element)?.BindingContext is not ProjectGuide project) return;
        await Shell.Current.GoToAsync($"{nameof(ProjectDetailPage)}?slug={project.Slug}");
    }
}
