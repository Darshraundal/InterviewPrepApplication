using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Interfaces;

public interface INoteService
{
    Task<UserNote?> GetNoteAsync(string userId, string questionId, string source);
    Task<IReadOnlyList<UserNote>> GetAllNotesAsync(string userId);
    Task<UserNote> SaveNoteAsync(string userId, string questionId, string source, string noteText);
    Task DeleteNoteAsync(int noteId, string userId);
}
