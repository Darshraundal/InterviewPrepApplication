using InterviewPrepPortal.Data;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.Services;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// ─────────────────────────────────────────────────────────────────────────────
// DATABASE — SQLite via EF Core (user data only; questions live in JSON files)
// Use an absolute path rooted at ContentRootPath so it works regardless of
// the process working directory (Azure App Service, VS, self-contained exe).
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    var rawCs = builder.Configuration.GetConnectionString("DefaultConnection") ?? "Data Source=interviewprep.db";
    // If the connection string is already absolute (contains :/ or :\) leave it.
    // Otherwise resolve it relative to ContentRootPath.
    if (!rawCs.Contains(":/") && !rawCs.Contains(@":\") && rawCs.StartsWith("Data Source="))
    {
        var dbFileName = rawCs["Data Source=".Length..].Trim();
        if (!Path.IsPathRooted(dbFileName))
        {
            var dbPath = Path.Combine(builder.Environment.ContentRootPath, dbFileName);
            rawCs = $"Data Source={dbPath}";
        }
    }
    options.UseSqlite(rawCs);
});

// ─────────────────────────────────────────────────────────────────────────────
// IDENTITY — ASP.NET Core Identity on top of SQLite
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddDefaultIdentity<ApplicationUser>(options =>
{
    options.Password.RequiredLength = 8;
    options.Password.RequireDigit = true;
    options.Password.RequireNonAlphanumeric = false;
    options.Password.RequireUppercase = false;
    options.SignIn.RequireConfirmedAccount = false;
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
})
.AddRoles<IdentityRole>()
.AddEntityFrameworkStores<ApplicationDbContext>();

// ─────────────────────────────────────────────────────────────────────────────
// CACHING — used by Singleton JSON services
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddMemoryCache();

// ─────────────────────────────────────────────────────────────────────────────
// DATA PROTECTION — persist keys to disk so auth cookies survive app restarts
// (on Azure F1 the instance sleeps/restarts; without this users get logged out)
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo(
        Path.Combine(builder.Environment.ContentRootPath, "DataProtectionKeys")));

// ─────────────────────────────────────────────────────────────────────────────
// COOKIE AUTH — redirect to custom Account controller, not Identity UI pages
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.ConfigureApplicationCookie(options =>
{
    options.LoginPath = "/Account/Login";
    options.LogoutPath = "/Account/Logout";
    options.AccessDeniedPath = "/Account/AccessDenied";
});

// ─────────────────────────────────────────────────────────────────────────────
// SERVICES — Singleton: read-only JSON loaders | Scoped: EF Core user data
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddSingleton<IQuestionService, QuestionService>();
builder.Services.AddSingleton<IProjectGuideService, ProjectGuideService>();
builder.Services.AddSingleton<ISearchService, SearchService>();

builder.Services.AddScoped<IProgressService, ProgressService>();
builder.Services.AddScoped<ICustomAnswerService, CustomAnswerService>();
builder.Services.AddScoped<INoteService, NoteService>();

// ─────────────────────────────────────────────────────────────────────────────
// MVC
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddControllersWithViews();
builder.Services.AddRazorPages(); // Required for Identity UI

var app = builder.Build();

// ─────────────────────────────────────────────────────────────────────────────
// AUTO-MIGRATE — Creates SQLite .db file and applies migrations on startup
// ─────────────────────────────────────────────────────────────────────────────
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    db.Database.Migrate();
}

// ─────────────────────────────────────────────────────────────────────────────
// MIDDLEWARE PIPELINE
// ─────────────────────────────────────────────────────────────────────────────
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.MapRazorPages();

app.Run();
