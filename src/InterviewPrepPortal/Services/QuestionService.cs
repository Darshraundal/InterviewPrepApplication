using System.Text.Json;
using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;
using Microsoft.Extensions.Caching.Memory;

namespace InterviewPrepPortal.Services;

/// <summary>
/// Singleton service — loads all question JSON files once at startup, caches in memory.
/// Zero DB access. All reads are O(1) from in-memory cache.
/// </summary>
public class QuestionService(IWebHostEnvironment env, IMemoryCache cache, ILogger<QuestionService> logger)
    : IQuestionService
{
    private const string CacheKeyAll = "questions_all";
    private const string CacheKeyCategories = "categories_all";
    private static readonly JsonSerializerOptions JsonOpts = new() { PropertyNameCaseInsensitive = true };

    // ---------------------------------------------------------------------------
    // Public interface implementation
    // ---------------------------------------------------------------------------

    public async Task<IReadOnlyList<Category>> GetCategoriesAsync()
    {
        var (cats, _) = await GetCachedDataAsync();
        return cats;
    }

    public async Task<Category?> GetCategoryBySlugAsync(string slug)
    {
        var cats = await GetCategoriesAsync();
        return cats.FirstOrDefault(c => c.Slug.Equals(slug, StringComparison.OrdinalIgnoreCase));
    }

    public async Task<Category?> GetCategoryByIdAsync(string id)
    {
        var cats = await GetCategoriesAsync();
        return cats.FirstOrDefault(c => c.Id.Equals(id, StringComparison.OrdinalIgnoreCase));
    }

    public async Task<IReadOnlyList<Question>> GetQuestionsByCategoryAsync(string categoryId)
    {
        var (_, questions) = await GetCachedDataAsync();
        return questions
            .Where(q => q.Category.Equals(categoryId, StringComparison.OrdinalIgnoreCase) && q.IsActive)
            .OrderBy(q => q.SortOrder)
            .ThenBy(q => q.Id)
            .ToList();
    }

    public async Task<Question?> GetQuestionByIdAsync(string questionId)
    {
        var (_, questions) = await GetCachedDataAsync();
        return questions.FirstOrDefault(q => q.Id.Equals(questionId, StringComparison.OrdinalIgnoreCase));
    }

    public async Task<IReadOnlyList<Question>> GetAllQuestionsAsync()
    {
        var (_, questions) = await GetCachedDataAsync();
        return questions.Where(q => q.IsActive).OrderBy(q => q.Category).ThenBy(q => q.SortOrder).ToList();
    }

    public async Task<IReadOnlyList<Question>> GetQuestionsByIdsAsync(IEnumerable<string> ids)
    {
        var (_, questions) = await GetCachedDataAsync();
        var idSet = new HashSet<string>(ids, StringComparer.OrdinalIgnoreCase);
        return questions.Where(q => idSet.Contains(q.Id)).ToList();
    }

    public async Task<IReadOnlyList<Question>> SearchQuestionsAsync(string query,
        string? categoryId = null, string? difficulty = null, string? frequency = null)
    {
        var (_, questions) = await GetCachedDataAsync();
        var q = query.ToLowerInvariant();

        return questions
            .Where(x => x.IsActive
                && (string.IsNullOrEmpty(categoryId) || x.Category.Equals(categoryId, StringComparison.OrdinalIgnoreCase))
                && (string.IsNullOrEmpty(difficulty) || x.Difficulty.Equals(difficulty, StringComparison.OrdinalIgnoreCase))
                && (string.IsNullOrEmpty(frequency) || x.Frequency.Equals(frequency, StringComparison.OrdinalIgnoreCase))
                && (string.IsNullOrEmpty(query) ||
                    x.QuestionText.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                    x.Answer.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                    x.Tags.Any(t => t.Contains(q, StringComparison.OrdinalIgnoreCase)) ||
                    (x.Tip != null && x.Tip.Contains(q, StringComparison.OrdinalIgnoreCase))))
            .OrderBy(x => x.Category)
            .ThenBy(x => x.SortOrder)
            .ToList();
    }

    // ---------------------------------------------------------------------------
    // Private cache loading
    // ---------------------------------------------------------------------------

    private async Task<(IReadOnlyList<Category> categories, IReadOnlyList<Question> questions)> GetCachedDataAsync()
    {
        if (cache.TryGetValue(CacheKeyCategories, out IReadOnlyList<Category>? cats) &&
            cache.TryGetValue(CacheKeyAll, out IReadOnlyList<Question>? qs))
        {
            return (cats!, qs!);
        }

        // Load fresh
        cats = await LoadCategoriesAsync();
        qs = await LoadAllQuestionsAsync();

        var opts = new MemoryCacheEntryOptions().SetSlidingExpiration(TimeSpan.FromHours(24));
        cache.Set(CacheKeyCategories, cats, opts);
        cache.Set(CacheKeyAll, qs, opts);

        return (cats, qs);
    }

    private async Task<List<Category>> LoadCategoriesAsync()
    {
        var path = Path.Combine(env.ContentRootPath, "Data", "JsonData", "categories.json");
        if (!File.Exists(path))
        {
            logger.LogWarning("categories.json not found at {Path}", path);
            return [];
        }

        await using var stream = File.OpenRead(path);
        var root = await JsonSerializer.DeserializeAsync<CategoriesRoot>(stream, JsonOpts);
        return root?.Categories ?? [];
    }

    private async Task<List<Question>> LoadAllQuestionsAsync()
    {
        var jsonDataPath = Path.Combine(env.ContentRootPath, "Data", "JsonData");
        if (!Directory.Exists(jsonDataPath)) return [];

        var allQuestions = new List<Question>();
        var files = Directory.GetFiles(jsonDataPath, "questions-*.json");

        foreach (var file in files)
        {
            try
            {
                await using var stream = File.OpenRead(file);
                var root = await JsonSerializer.DeserializeAsync<QuestionsFile>(stream, JsonOpts);
                if (root?.Questions != null)
                {
                    allQuestions.AddRange(root.Questions);
                    logger.LogInformation("Loaded {Count} questions from {File}", root.Questions.Count, Path.GetFileName(file));
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Failed to load questions from {File}", file);
            }
        }

        return allQuestions;
    }
}
