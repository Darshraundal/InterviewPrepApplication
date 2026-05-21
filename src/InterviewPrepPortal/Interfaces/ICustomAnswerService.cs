using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Interfaces;

public interface ICustomAnswerService
{
    Task<UserCustomAnswer?> GetCustomAnswerAsync(string userId, string questionId, string source);
    Task<IReadOnlyList<UserCustomAnswer>> GetAllCustomAnswersAsync(string userId);
    Task<UserCustomAnswer> SaveCustomAnswerAsync(string userId, string questionId, string source, string answerText);
    Task DeleteCustomAnswerAsync(string userId, string questionId, string source);
}
