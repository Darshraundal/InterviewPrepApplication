using InterviewPrepPortal.Data;
using InterviewPrepPortal.Mobile.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace InterviewPrepPortal.Mobile;

public partial class App : Application
{
    public App(IServiceProvider services)
    {
        InitializeComponent();

        // One-time setup before any UI is shown: extract bundled question/project
        // JSON into app-local storage, then create the local SQLite DB if missing.
        // Both are fast (sub-second) after the very first launch, so blocking here
        // is acceptable — there is no UI yet to freeze.
        JsonDataSeeder.EnsureSeededAsync().GetAwaiter().GetResult();

        using var scope = services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<LocalDbContext>();
        db.Database.EnsureCreated();

        MainPage = services.GetRequiredService<AppShell>();
    }
}
