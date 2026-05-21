using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.ViewModels.Category;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class CategoryController(
    IQuestionService questionService,
    IProgressService progressService,
    ICustomAnswerService customAnswerService,
    INoteService noteService,
    UserManager<ApplicationUser> userManager) : Controller
{
    public async Task<IActionResult> Index()
    {
        var user = await userManager.GetUserAsync(User);
        var categories = await questionService.GetCategoriesAsync();
        var allQuestions = await questionService.GetAllQuestionsAsync();

        var items = new List<CategoryWithStats>();
        foreach (var cat in categories.Where(c => c.IsActive).OrderBy(c => c.SortOrder))
        {
            var total = allQuestions.Count(q => q.Category == cat.Id);
            CategoryProgressSummary? progress = null;

            if (user != null)
                progress = await progressService.GetCategoryProgressAsync(user.Id, cat.Id);

            items.Add(new CategoryWithStats
            {
                Category = cat,
                TotalQuestions = total,
                Progress = progress
            });
        }

        return View(new CategoryListViewModel { Categories = items });
    }

    public async Task<IActionResult> Detail(string slug,
        string? q = null, string? difficulty = null,
        string? frequency = null, string? status = null)
    {
        var category = await questionService.GetCategoryBySlugAsync(slug);
        if (category == null) return NotFound();

        var user = await userManager.GetUserAsync(User);
        var userId = user?.Id ?? string.Empty;

        // Load questions with optional server-side filters
        var questions = string.IsNullOrWhiteSpace(q) && string.IsNullOrWhiteSpace(difficulty) && string.IsNullOrWhiteSpace(frequency)
            ? await questionService.GetQuestionsByCategoryAsync(category.Id)
            : await questionService.SearchQuestionsAsync(q ?? string.Empty, category.Id, difficulty, frequency);

        var totalCount = (await questionService.GetQuestionsByCategoryAsync(category.Id)).Count;

        // Get status map for efficient lookup
        var statusMap = userId.Length > 0
            ? await progressService.GetStatusMapAsync(userId, category.Id)
            : new Dictionary<string, ProgressStatus>();

        // Apply status filter after DB lookup
        var filteredQuestions = questions.AsEnumerable();
        if (!string.IsNullOrWhiteSpace(status) && userId.Length > 0)
        {
            filteredQuestions = status switch
            {
                "mastered" => filteredQuestions.Where(x => statusMap.TryGetValue(x.Id, out var s) && s == ProgressStatus.Mastered),
                "learning" => filteredQuestions.Where(x => statusMap.TryGetValue(x.Id, out var s) && s == ProgressStatus.Learning),
                "not-started" => filteredQuestions.Where(x => !statusMap.ContainsKey(x.Id) || statusMap[x.Id] == ProgressStatus.NotStarted),
                _ => filteredQuestions
            };
        }

        var questionList = filteredQuestions.ToList();

        // Build QuestionWithUserData — check which ones have notes/answers
        var items = new List<QuestionWithUserData>();
        foreach (var question in questionList)
        {
            var progress = userId.Length > 0
                ? await progressService.GetProgressAsync(userId, question.Id, "category")
                : null;

            var hasCustomAnswer = userId.Length > 0 &&
                (await customAnswerService.GetCustomAnswerAsync(userId, question.Id, "category")) != null;

            var hasNote = userId.Length > 0 &&
                (await noteService.GetNoteAsync(userId, question.Id, "category")) != null;

            items.Add(new QuestionWithUserData
            {
                Question = question,
                Progress = progress,
                HasCustomAnswer = hasCustomAnswer,
                HasNote = hasNote
            });
        }

        var categoryProgress = userId.Length > 0
            ? await progressService.GetCategoryProgressAsync(userId, category.Id)
            : new CategoryProgressSummary(category.Id, 0, 0, 0, 0);

        var vm = new CategoryDetailViewModel
        {
            Category = category,
            Questions = items,
            Progress = categoryProgress,
            SearchQuery = q,
            DifficultyFilter = difficulty,
            FrequencyFilter = frequency,
            StatusFilter = status,
            TotalCount = totalCount,
            FilteredCount = questionList.Count
        };

        return View(vm);
    }
}
