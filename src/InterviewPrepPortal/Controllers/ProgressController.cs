using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.ViewModels.Category;
using InterviewPrepPortal.ViewModels.Progress;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class ProgressController(
    IProgressService progressService,
    IQuestionService questionService,
    INoteService noteService,
    UserManager<ApplicationUser> userManager) : Controller
{
    public async Task<IActionResult> Index()
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Challenge();

        var overallTask = progressService.GetProgressSummaryAsync(user.Id);
        var allCatsTask = questionService.GetCategoriesAsync();
        var allQuestionsTask = questionService.GetAllQuestionsAsync();
        var notesTask = noteService.GetAllNotesAsync(user.Id);
        var revisionTask = progressService.GetRevisionQueueAsync(user.Id);
        var favoritesTask = progressService.GetFavoritesAsync(user.Id);

        await Task.WhenAll(overallTask, allCatsTask, allQuestionsTask, notesTask, revisionTask, favoritesTask);

        var overall = await overallTask;
        var allCats = await allCatsTask;
        var allQuestions = await allQuestionsTask;
        var notes = await notesTask;
        var revision = await revisionTask;
        var favorites = await favoritesTask;

        // Per-category breakdown
        var perCategory = new List<CategoryProgressItem>();
        foreach (var cat in allCats.Where(c => c.IsActive).OrderBy(c => c.SortOrder))
        {
            var summary = await progressService.GetCategoryProgressAsync(user.Id, cat.Id);
            perCategory.Add(new CategoryProgressItem
            {
                CategoryId = cat.Id,
                CategoryName = cat.Name,
                Emoji = cat.Emoji,
                Summary = summary,
                TotalQuestions = allQuestions.Count(q => q.Category == cat.Id)
            });
        }

        // Build revision queue with question text
        var revisionItems = revision.Select(p => new QuestionWithUserData
        {
            Question = allQuestions.FirstOrDefault(q => q.Id == p.QuestionId)!,
            Progress = p
        }).Where(x => x.Question != null).ToList();

        // Build favorites with question text
        var favoriteItems = favorites.Select(p => new QuestionWithUserData
        {
            Question = allQuestions.FirstOrDefault(q => q.Id == p.QuestionId)!,
            Progress = p
        }).Where(x => x.Question != null).ToList();

        var vm = new ProgressDashboardViewModel
        {
            Overall = overall,
            PerCategory = perCategory,
            RevisionQueue = revisionItems,
            Favorites = favoriteItems,
            RecentNotes = notes.Take(10).ToList()
        };

        return View(vm);
    }

    public async Task<IActionResult> RevisionQueue()
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Challenge();

        var revision = await progressService.GetRevisionQueueAsync(user.Id);
        var allQuestions = await questionService.GetAllQuestionsAsync();

        var items = revision.Select(p => new QuestionWithUserData
        {
            Question = allQuestions.FirstOrDefault(q => q.Id == p.QuestionId)!,
            Progress = p
        }).Where(x => x.Question != null).ToList();

        return View(items);
    }

    public async Task<IActionResult> Favorites()
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Challenge();

        var favorites = await progressService.GetFavoritesAsync(user.Id);
        var allQuestions = await questionService.GetAllQuestionsAsync();

        var items = favorites.Select(p => new QuestionWithUserData
        {
            Question = allQuestions.FirstOrDefault(q => q.Id == p.QuestionId)!,
            Progress = p
        }).Where(x => x.Question != null).ToList();

        return View(items);
    }
}
