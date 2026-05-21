using System.Diagnostics;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.ViewModels.Home;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class HomeController(
    IQuestionService questionService,
    IProjectGuideService projectGuideService,
    IProgressService progressService,
    UserManager<ApplicationUser> userManager,
    ILogger<HomeController> logger) : Controller
{
    public async Task<IActionResult> Index()
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Challenge();

        var categoriesTask = questionService.GetCategoriesAsync();
        var allQuestionsTask = questionService.GetAllQuestionsAsync();
        var projectsTask = projectGuideService.GetAllProjectsAsync();
        var progressSummaryTask = progressService.GetProgressSummaryAsync(user.Id);
        var revisionTask = progressService.GetRevisionQueueAsync(user.Id);
        var favoritesTask = progressService.GetFavoritesAsync(user.Id);

        await Task.WhenAll(categoriesTask, allQuestionsTask, projectsTask,
            progressSummaryTask, revisionTask, favoritesTask);

        var categories = await categoriesTask;
        var allQuestions = await allQuestionsTask;
        var projects = await projectsTask;
        var summary = await progressSummaryTask;
        var revisionProgress = await revisionTask;
        var favoritesProgress = await favoritesTask;

        // Build category-with-progress list
        var categoryItems = new List<CategoryWithProgress>();
        foreach (var cat in categories.Where(c => c.IsActive).OrderBy(c => c.SortOrder))
        {
            var catProgress = await progressService.GetCategoryProgressAsync(user.Id, cat.Id);
            var totalInCat = allQuestions.Count(q => q.Category == cat.Id);
            categoryItems.Add(new CategoryWithProgress
            {
                Category = cat,
                Progress = catProgress,
                TotalQuestions = totalInCat
            });
        }

        // Build revision queue display items (top 8)
        var revisionItems = revisionProgress.Take(8).Select(p => new QuestionWithProgress
        {
            QuestionId = p.QuestionId,
            QuestionText = allQuestions.FirstOrDefault(q => q.Id == p.QuestionId)?.QuestionText ?? p.QuestionId,
            CategoryId = p.QuestionSource,
            Source = p.QuestionSource,
            Progress = p
        }).ToList();

        // Build favorites display items (top 5)
        var favoriteItems = favoritesProgress.Take(5).Select(p => new QuestionWithProgress
        {
            QuestionId = p.QuestionId,
            QuestionText = allQuestions.FirstOrDefault(q => q.Id == p.QuestionId)?.QuestionText ?? p.QuestionId,
            CategoryId = p.QuestionSource,
            Source = p.QuestionSource,
            Progress = p
        }).ToList();

        var vm = new DashboardViewModel
        {
            UserDisplayName = user.DisplayName,
            OverallProgress = summary,
            Categories = categoryItems,
            Projects = projects.ToList(),
            RevisionQueue = revisionItems,
            RecentFavorites = favoriteItems,
            TotalCategoryQuestions = allQuestions.Count,
            TotalProjectQuestions = summary.TotalProjectQuestions
        };

        return View(vm);
    }

    [AllowAnonymous]
    public IActionResult About() => View();

    [AllowAnonymous]
    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
