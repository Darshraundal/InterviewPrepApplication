using InterviewPrepPortal.Data;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using Microsoft.EntityFrameworkCore;

namespace InterviewPrepPortal.Services;

public class NoteService(ApplicationDbContext db) : INoteService
{
    public async Task<UserNote?> GetNoteAsync(string userId, string questionId, string source)
    {
        return await db.UserNotes
            .FirstOrDefaultAsync(n => n.UserId == userId && n.QuestionId == questionId && n.QuestionSource == source);
    }

    public async Task<IReadOnlyList<UserNote>> GetAllNotesAsync(string userId)
    {
        return await db.UserNotes
            .Where(n => n.UserId == userId)
            .OrderByDescending(n => n.UpdatedAt)
            .ToListAsync();
    }

    public async Task<UserNote> SaveNoteAsync(string userId, string questionId, string source, string noteText)
    {
        var existing = await GetNoteAsync(userId, questionId, source);

        if (existing != null)
        {
            existing.NoteText = noteText;
            existing.UpdatedAt = DateTime.UtcNow;
        }
        else
        {
            existing = new UserNote
            {
                UserId = userId,
                QuestionId = questionId,
                QuestionSource = source,
                NoteText = noteText
            };
            db.UserNotes.Add(existing);
        }

        await db.SaveChangesAsync();
        return existing;
    }

    public async Task DeleteNoteAsync(int noteId, string userId)
    {
        var note = await db.UserNotes.FirstOrDefaultAsync(n => n.Id == noteId && n.UserId == userId);
        if (note != null)
        {
            db.UserNotes.Remove(note);
            await db.SaveChangesAsync();
        }
    }
}
