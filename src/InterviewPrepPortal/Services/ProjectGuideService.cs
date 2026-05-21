using System.Text.Json;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;
using Microsoft.Extensions.Caching.Memory;

namespace InterviewPrepPortal.Services;

/// <summary>
/// Singleton service — loads project guides from JSON once at startup, caches in memory.
/// </summary>
public class ProjectGuideService(IWebHostEnvironment env, IMemoryCache cache, ILogger<ProjectGuideService> logger)
    : IProjectGuideService
{
    private const string CacheKeyIndex = "projects_index";
    private const string CacheKeyDetails = "projects_details";
    private static readonly JsonSerializerOptions JsonOpts = new() { PropertyNameCaseInsensitive = true };

    public async Task<IReadOnlyList<ProjectGuide>> GetAllProjectsAsync()
    {
        var (index, _) = await GetCachedDataAsync();
        return index.Where(p => p.IsActive).OrderBy(p => p.SortOrder).ToList();
    }

    public async Task<ProjectGuide?> GetProjectBySlugAsync(string slug)
    {
        var projects = await GetAllProjectsAsync();
        return projects.FirstOrDefault(p => p.Slug.Equals(slug, StringComparison.OrdinalIgnoreCase));
    }

    public async Task<ProjectDetail?> GetProjectDetailAsync(string slug)
    {
        var (_, details) = await GetCachedDataAsync();
        return details.TryGetValue(slug.ToLowerInvariant(), out var detail) ? detail : null;
    }

    public async Task<IReadOnlyList<ProjectQuestion>> GetQuestionsByProjectAsync(string projectId)
    {
        var detail = await GetProjectDetailAsync(projectId);
        return detail?.Questions
            .Where(q => q.IsActive)
            .OrderBy(q => q.SortOrder)
            .ThenBy(q => q.Id)
            .ToList() ?? [];
    }

    public async Task<ProjectQuestion?> GetProjectQuestionByIdAsync(string questionId)
    {
        var (_, details) = await GetCachedDataAsync();
        foreach (var d in details.Values)
        {
            var q = d.Questions.FirstOrDefault(x => x.Id.Equals(questionId, StringComparison.OrdinalIgnoreCase));
            if (q != null) return q;
        }
        return null;
    }

    public async Task<IReadOnlyList<ProjectQuestion>> SearchProjectQuestionsAsync(string query, string? projectId = null)
    {
        var (_, details) = await GetCachedDataAsync();
        var q = query.ToLowerInvariant();

        IEnumerable<ProjectQuestion> source = projectId != null && details.TryGetValue(projectId.ToLowerInvariant(), out var pd)
            ? pd.Questions
            : details.Values.SelectMany(d => d.Questions);

        return source
            .Where(x => x.IsActive && (
                string.IsNullOrEmpty(query) ||
                x.QuestionText.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                x.Answer.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                x.Tags.Any(t => t.Contains(q, StringComparison.OrdinalIgnoreCase))))
            .OrderBy(x => x.ProjectId)
            .ThenBy(x => x.SortOrder)
            .ToList();
    }

    // ---------------------------------------------------------------------------
    // Private cache loading
    // ---------------------------------------------------------------------------

    private async Task<(IReadOnlyList<ProjectGuide> index, Dictionary<string, ProjectDetail> details)> GetCachedDataAsync()
    {
        if (cache.TryGetValue(CacheKeyIndex, out IReadOnlyList<ProjectGuide>? idx) &&
            cache.TryGetValue(CacheKeyDetails, out Dictionary<string, ProjectDetail>? dets))
        {
            return (idx!, dets!);
        }

        idx = await LoadProjectIndexAsync();
        dets = await LoadProjectDetailsAsync(idx);

        var opts = new MemoryCacheEntryOptions().SetSlidingExpiration(TimeSpan.FromHours(24));
        cache.Set(CacheKeyIndex, idx, opts);
        cache.Set(CacheKeyDetails, dets, opts);

        return (idx, dets);
    }

    private async Task<List<ProjectGuide>> LoadProjectIndexAsync()
    {
        var path = Path.Combine(env.ContentRootPath, "Data", "JsonData", "projects", "projects-index.json");
        if (!File.Exists(path))
        {
            logger.LogWarning("projects-index.json not found at {Path}", path);
            return [];
        }

        await using var stream = File.OpenRead(path);
        var root = await JsonSerializer.DeserializeAsync<ProjectsIndex>(stream, JsonOpts);
        return root?.Projects ?? [];
    }

    private async Task<Dictionary<string, ProjectDetail>> LoadProjectDetailsAsync(IReadOnlyList<ProjectGuide> index)
    {
        var result = new Dictionary<string, ProjectDetail>();
        var baseDir = Path.Combine(env.ContentRootPath, "Data", "JsonData", "projects");

        foreach (var project in index)
        {
            var filePath = Path.Combine(env.ContentRootPath, "Data", "JsonData", project.DataFile);
            if (!File.Exists(filePath))
            {
                logger.LogWarning("Project data file not found: {File}", project.DataFile);
                continue;
            }

            try
            {
                await using var stream = File.OpenRead(filePath);
                var detail = await JsonSerializer.DeserializeAsync<ProjectDetail>(stream, JsonOpts);
                if (detail != null)
                {
                    result[project.Slug.ToLowerInvariant()] = detail;
                    logger.LogInformation("Loaded {Count} questions for project {Project}",
                        detail.Questions.Count, project.Name);
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Failed to load project detail for {Project}", project.Slug);
            }
        }

        return result;
    }
}
