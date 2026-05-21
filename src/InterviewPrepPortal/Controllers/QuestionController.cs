using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using InterviewPrepPortal.ViewModels.Question;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class QuestionController(
    IQuestionService questionService,
    IProgressService progressService,
    ICustomAnswerService customAnswerService,
    INoteService noteService,
    UserManager<ApplicationUser> userManager) : Controller
{
    // ── DETAIL ───────────────────────────────────────────────────────────────

    [HttpGet]
    public async Task<IActionResult> Detail(string id)
    {
        var question = await questionService.GetQuestionByIdAsync(id);
        if (question == null) return NotFound();

        var category = await questionService.GetCategoryByIdAsync(question.Category);
        if (category == null) return NotFound();

        var user = await userManager.GetUserAsync(User);
        var userId = user?.Id ?? string.Empty;

        // Load sibling questions for prev/next navigation
        var siblings = await questionService.GetQuestionsByCategoryAsync(question.Category);
        var idx = siblings.ToList().FindIndex(q => q.Id == question.Id);

        var progress = userId.Length > 0 ? await progressService.GetProgressAsync(userId, id, "category") : null;
        var customAnswer = userId.Length > 0 ? await customAnswerService.GetCustomAnswerAsync(userId, id, "category") : null;
        var note = userId.Length > 0 ? await noteService.GetNoteAsync(userId, id, "category") : null;

        // Load cross-referenced questions
        var crossRefs = question.CrossReferenceIds.Count > 0
            ? (await questionService.GetQuestionsByIdsAsync(question.CrossReferenceIds)).ToList()
            : [];

        var vm = new QuestionDetailViewModel
        {
            Question = question,
            Category = category,
            Progress = progress,
            CustomAnswer = customAnswer,
            Note = note,
            CrossReferences = crossRefs,
            PreviousQuestion = idx > 0 ? siblings[idx - 1] : null,
            NextQuestion = idx < siblings.Count - 1 ? siblings[idx + 1] : null
        };

        return View(vm);
    }

    // ── AJAX: UPDATE PROGRESS ─────────────────────────────────────────────────

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> UpdateProgress(
        string questionId, string source,
        ProgressStatus status, ConfidenceLevel confidence,
        bool revisionNeeded, bool isFavorite)
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Unauthorized();

        try
        {
            await progressService.UpsertProgressAsync(
                user.Id, questionId, source, status, confidence, revisionNeeded, isFavorite);

            return Json(new { success = true, message = "Progress saved." });
        }
        catch (Exception ex)
        {
            return Json(new { success = false, message = ex.Message });
        }
    }

    // ── AJAX: SAVE CUSTOM ANSWER ──────────────────────────────────────────────

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> SaveCustomAnswer(string questionId, string source, string answerText)
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Unauthorized();

        try
        {
            await customAnswerService.SaveCustomAnswerAsync(user.Id, questionId, source, answerText);
            return Json(new { success = true, message = "Answer saved." });
        }
        catch (Exception ex)
        {
            return Json(new { success = false, message = ex.Message });
        }
    }

    // ── AJAX: SAVE NOTE ───────────────────────────────────────────────────────

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> SaveNote(string questionId, string source, string noteText)
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Unauthorized();

        try
        {
            await noteService.SaveNoteAsync(user.Id, questionId, source, noteText);
            return Json(new { success = true, message = "Note saved." });
        }
        catch (Exception ex)
        {
            return Json(new { success = false, message = ex.Message });
        }
    }

    // ── AJAX: TOGGLE FAVORITE ─────────────────────────────────────────────────

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> ToggleFavorite(string questionId, string source, bool isFavorite)
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Unauthorized();

        try
        {
            var progress = await progressService.GetProgressAsync(user.Id, questionId, source)
                ?? new UserProgress { Status = ProgressStatus.NotStarted, Confidence = ConfidenceLevel.None };

            await progressService.UpsertProgressAsync(
                user.Id, questionId, source,
                progress.Status, progress.Confidence,
                progress.IsRevisionNeeded, isFavorite);

            return Json(new { success = true, isFavorite });
        }
        catch (Exception ex)
        {
            return Json(new { success = false, message = ex.Message });
        }
    }
}
