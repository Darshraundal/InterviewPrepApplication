using InterviewPrepPortal.Models;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace InterviewPrepPortal.Data;

public class ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
    : IdentityDbContext<ApplicationUser>(options)
{
    public DbSet<UserProgress> UserProgresses { get; set; }
    public DbSet<UserCustomAnswer> UserCustomAnswers { get; set; }
    public DbSet<UserNote> UserNotes { get; set; }
    public DbSet<UserFavorite> UserFavorites { get; set; }

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        // One progress record per user per question (category or project)
        builder.Entity<UserProgress>()
            .HasIndex(p => new { p.UserId, p.QuestionId, p.QuestionSource })
            .IsUnique();

        // One custom answer per user per question
        builder.Entity<UserCustomAnswer>()
            .HasIndex(a => new { a.UserId, a.QuestionId, a.QuestionSource })
            .IsUnique();

        // One note per user per question
        builder.Entity<UserNote>()
            .HasIndex(n => new { n.UserId, n.QuestionId, n.QuestionSource })
            .IsUnique();

        // One favorite record per user per question
        builder.Entity<UserFavorite>()
            .HasIndex(f => new { f.UserId, f.QuestionId, f.QuestionSource })
            .IsUnique();
    }
}
