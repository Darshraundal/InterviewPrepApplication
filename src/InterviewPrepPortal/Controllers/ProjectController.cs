using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.ViewModels.Project;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class ProjectController(
    IProjectGuideService projectGuideService,
    IProgressService progressService,
    ICustomAnswerService customAnswerService,
    INoteService noteService,
    UserManager<ApplicationUser> userManager) : Controller
{
    public async Task<IActionResult> Index()
    {
        var projects = await projectGuideService.GetAllProjectsAsync();
        return View(new ProjectListViewModel { Projects = projects.ToList() });
    }

    public async Task<IActionResult> Detail(string slug, string? section = null, string? q = null)
    {
        var project = await projectGuideService.GetProjectBySlugAsync(slug);
        if (project == null) return NotFound();

        var detail = await projectGuideService.GetProjectDetailAsync(slug);
        if (detail == null) return NotFound();

        var user = await userManager.GetUserAsync(User);
        var userId = user?.Id ?? string.Empty;

        var allQuestions = detail.Questions.Where(x => x.IsActive).ToList();

        // Apply section and search filters
        var filtered = allQuestions.AsEnumerable();
        if (!string.IsNullOrWhiteSpace(section))
            filtered = filtered.Where(x => x.Section.Equals(section, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrWhiteSpace(q))
            filtered = filtered.Where(x =>
                x.QuestionText.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                x.Answer.Contains(q, StringComparison.OrdinalIgnoreCase));

        var filteredList = filtered.OrderBy(x => x.SortOrder).ToList();

        // Build sections with questions
        var sections = new List<ProjectSectionWithQuestions>();
        var sectionGroups = detail.Sections.OrderBy(s => s.SortOrder).ToList();

        foreach (var sec in sectionGroups)
        {
            var secQuestions = filteredList.Where(x => x.Section == sec.Id).ToList();
            if (secQuestions.Count == 0 && !string.IsNullOrWhiteSpace(section)) continue;

            var secItems = new List<ProjectQuestionWithUserData>();
            foreach (var pq in secQuestions)
            {
                var progress = userId.Length > 0
                    ? await progressService.GetProgressAsync(userId, pq.Id, "project")
                    : null;

                var hasCustomAnswer = userId.Length > 0 &&
                    (await customAnswerService.GetCustomAnswerAsync(userId, pq.Id, "project")) != null;

                var hasNote = userId.Length > 0 &&
                    (await noteService.GetNoteAsync(userId, pq.Id, "project")) != null;

                secItems.Add(new ProjectQuestionWithUserData
                {
                    Question = pq,
                    Progress = progress,
                    HasCustomAnswer = hasCustomAnswer,
                    HasNote = hasNote
                });
            }

            sections.Add(new ProjectSectionWithQuestions
            {
                Section = sec,
                Questions = secItems
            });
        }

        // Count progress
        var allProgress = userId.Length > 0 ? await progressService.GetAllProgressAsync(userId) : [];
        var masteredCount = allProgress
            .Count(p => p.QuestionSource == "project" && p.ProjectId() == slug && p.Status == ProgressStatus.Mastered);

        var vm = new ProjectDetailViewModel
        {
            Project = project,
            Detail = detail,
            Sections = sections,
            TotalQuestions = allQuestions.Count,
            MasteredCount = masteredCount,
            ActiveSection = section,
            SearchQuery = q
        };

        return View(vm);
    }
}

// Extension method to extract project ID from a progress record
public static class UserProgressExtensions
{
    public static string ProjectId(this UserProgress p)
    {
        // Project question IDs are formatted as "projectslug-section-NNN"
        // We take the first segment
        var parts = p.QuestionId.Split('-');
        return parts.Length > 0 ? parts[0] : string.Empty;
    }
}
