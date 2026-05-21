using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace InterviewPrepPortal.Controllers;

[Authorize]
public class NoteController(
    INoteService noteService,
    UserManager<ApplicationUser> userManager) : Controller
{
    public async Task<IActionResult> Index()
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Challenge();

        var notes = await noteService.GetAllNotesAsync(user.Id);
        return View(notes);
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int noteId)
    {
        var user = await userManager.GetUserAsync(User);
        if (user == null) return Unauthorized();

        await noteService.DeleteNoteAsync(noteId, user.Id);
        return RedirectToAction(nameof(Index));
    }
}
