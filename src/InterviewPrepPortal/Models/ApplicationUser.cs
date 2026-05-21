using Microsoft.AspNetCore.Identity;

namespace InterviewPrepPortal.Models;

public class ApplicationUser : IdentityUser
{
    public string DisplayName { get; set; } = string.Empty;
    public DateTime RegisteredAt { get; set; } = DateTime.UtcNow;
    public DateTime? LastLoginAt { get; set; }

    // Navigation
    public ICollection<UserProgress> Progresses { get; set; } = [];
    public ICollection<UserCustomAnswer> CustomAnswers { get; set; } = [];
    public ICollection<UserNote> Notes { get; set; } = [];
    public ICollection<UserFavorite> Favorites { get; set; } = [];
}
