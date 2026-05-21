using InterviewPrepPortal.Data;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.Models;
using Microsoft.EntityFrameworkCore;

namespace InterviewPrepPortal.Services;

public class CustomAnswerService(ApplicationDbContext db) : ICustomAnswerService
{
    public async Task<UserCustomAnswer?> GetCustomAnswerAsync(string userId, string questionId, string source)
    {
        return await db.UserCustomAnswers
            .FirstOrDefaultAsync(a => a.UserId == userId && a.QuestionId == questionId && a.QuestionSource == source);
    }

    public async Task<IReadOnlyList<UserCustomAnswer>> GetAllCustomAnswersAsync(string userId)
    {
        return await db.UserCustomAnswers
            .Where(a => a.UserId == userId)
            .OrderByDescending(a => a.UpdatedAt)
            .ToListAsync();
    }

    public async Task<UserCustomAnswer> SaveCustomAnswerAsync(string userId, string questionId, string source, string answerText)
    {
        var existing = await GetCustomAnswerAsync(userId, questionId, source);

        if (existing != null)
        {
            existing.AnswerText = answerText;
            existing.UpdatedAt = DateTime.UtcNow;
        }
        else
        {
            existing = new UserCustomAnswer
            {
                UserId = userId,
                QuestionId = questionId,
                QuestionSource = source,
                AnswerText = answerText
            };
            db.UserCustomAnswers.Add(existing);
        }

        await db.SaveChangesAsync();
        return existing;
    }

    public async Task DeleteCustomAnswerAsync(string userId, string questionId, string source)
    {
        var answer = await GetCustomAnswerAsync(userId, questionId, source);
        if (answer != null)
        {
            db.UserCustomAnswers.Remove(answer);
            await db.SaveChangesAsync();
        }
    }
}
