using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Services;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class CategoriesViewModel(IQuestionService questionService, IProgressService progressService) : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    public ObservableCollection<CategoryProgressRowViewModel> Categories { get; } = [];

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            Categories.Clear();
            var cats = (await questionService.GetCategoriesAsync()).OrderBy(c => c.SortOrder);
            foreach (var cat in cats)
            {
                var summary = await progressService.GetCategoryProgressAsync(LocalUser.Id, cat.Id);
                var total = (await questionService.GetQuestionsByCategoryAsync(cat.Id)).Count;
                Categories.Add(new CategoryProgressRowViewModel { Category = cat, Mastered = summary.Mastered, Total = total });
            }
        }
        finally
        {
            IsBusy = false;
        }
    }
}
