using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.Mobile.ViewModels;

public partial class ProjectsViewModel(IProjectGuideService projectGuideService) : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    public ObservableCollection<ProjectGuide> Projects { get; } = [];

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        try
        {
            var projects = (await projectGuideService.GetAllProjectsAsync())
                .OrderBy(p => p.SortOrder)
                .ToList();

            Projects.Clear();
            foreach (var p in projects)
                Projects.Add(p);
        }
        finally
        {
            IsBusy = false;
        }
    }
}
