using InterviewPrepPortal.Mobile.ViewModels;

namespace InterviewPrepPortal.Mobile.Pages;

public partial class CategoriesPage : ContentPage
{
    private readonly CategoriesViewModel _viewModel;

    public CategoriesPage(CategoriesViewModel viewModel)
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
}
