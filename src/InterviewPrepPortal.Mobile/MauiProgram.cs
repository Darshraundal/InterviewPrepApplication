using InterviewPrepPortal.Data;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Mobile.Pages;
using InterviewPrepPortal.Mobile.Services;
using InterviewPrepPortal.Mobile.ViewModels;
using InterviewPrepPortal.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace InterviewPrepPortal.Mobile;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>();

        // ─────────────────────────────────────────────────────────────────
        // SHARED CORE — same JSON-backed read services used by the web app
        // ─────────────────────────────────────────────────────────────────
        builder.Services.AddMemoryCache();
        builder.Services.AddSingleton<IJsonDataLocator, MobileJsonDataLocator>();
        builder.Services.AddSingleton<IQuestionService, QuestionService>();
        builder.Services.AddSingleton<IProjectGuideService, ProjectGuideService>();
        builder.Services.AddSingleton<ISearchService, SearchService>();

        // ─────────────────────────────────────────────────────────────────
        // LOCAL SQLITE — user progress/notes/answers, fully on-device, no network
        // ─────────────────────────────────────────────────────────────────
        var dbPath = Path.Combine(FileSystem.AppDataDirectory, "interviewprep.db");
        builder.Services.AddDbContext<LocalDbContext>(options => options.UseSqlite($"Data Source={dbPath}"));

        builder.Services.AddTransient<IProgressService, ProgressService>();
        builder.Services.AddTransient<ICustomAnswerService, CustomAnswerService>();
        builder.Services.AddTransient<INoteService, NoteService>();

        // ─────────────────────────────────────────────────────────────────
        // PAGES + VIEWMODELS
        // ─────────────────────────────────────────────────────────────────
        builder.Services.AddSingleton<AppShell>();

        builder.Services.AddTransient<HomePage>();
        builder.Services.AddTransient<HomeViewModel>();

        builder.Services.AddTransient<CategoriesPage>();
        builder.Services.AddTransient<CategoriesViewModel>();

        builder.Services.AddTransient<CategoryDetailPage>();
        builder.Services.AddTransient<CategoryDetailViewModel>();

        builder.Services.AddTransient<QuestionDetailPage>();
        builder.Services.AddTransient<QuestionDetailViewModel>();

        builder.Services.AddTransient<ProjectsPage>();
        builder.Services.AddTransient<ProjectsViewModel>();

        builder.Services.AddTransient<ProjectDetailPage>();
        builder.Services.AddTransient<ProjectDetailViewModel>();

        builder.Services.AddTransient<SearchPage>();
        builder.Services.AddTransient<SearchViewModel>();

        builder.Services.AddTransient<ProgressPage>();
        builder.Services.AddTransient<ProgressViewModel>();

        builder.Services.AddTransient<FavoritesPage>();
        builder.Services.AddTransient<FavoritesViewModel>();

        builder.Services.AddTransient<RevisionQueuePage>();
        builder.Services.AddTransient<RevisionQueueViewModel>();

        builder.Services.AddTransient<NotesPage>();
        builder.Services.AddTransient<NotesViewModel>();

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}
