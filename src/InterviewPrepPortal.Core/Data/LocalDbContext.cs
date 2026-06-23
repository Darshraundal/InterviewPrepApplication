using InterviewPrepPortal.Models;
using Microsoft.EntityFrameworkCore;

namespace InterviewPrepPortal.Data;

/// <summary>
/// On-device EF Core SQLite context for the mobile app. Unlike the web app's
/// ApplicationDbContext, this has no ASP.NET Identity tables — the mobile app
/// runs as a single local user, so UserId is just a plain string column.
/// </summary>
public class LocalDbContext(DbContextOptions<LocalDbContext> options) : DbContext(options)
{
    public DbSet<UserProgress> UserProgresses { get; set; }
    public DbSet<UserCustomAnswer> UserCustomAnswers { get; set; }
    public DbSet<UserNote> UserNotes { get; set; }

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        builder.Entity<UserProgress>()
            .HasIndex(p => new { p.UserId, p.QuestionId, p.QuestionSource })
            .IsUnique();

        builder.Entity<UserCustomAnswer>()
            .HasIndex(a => new { a.UserId, a.QuestionId, a.QuestionSource })
            .IsUnique();

        builder.Entity<UserNote>()
            .HasIndex(n => new { n.UserId, n.QuestionId, n.QuestionSource })
            .IsUnique();
    }
}
